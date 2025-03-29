import re
import numpy as np
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from paddleocr import PaddleOCR
import cv2
from fastapi.middleware.cors import CORSMiddleware
import traceback
import time
import os
from starlette.requests import Request
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("paddleocr-api")

# Configure API settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
RATE_LIMIT_REQUESTS = 10  # Number of requests allowed
RATE_LIMIT_WINDOW = 60  # Time window in seconds

app = FastAPI(title="PaddleOCR API", version="1.0.0")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory rate limiter
class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.clients: Dict[str, list] = {}

    def is_rate_limited(self, client_id: str) -> bool:
        current_time = time.time()
        
        # Initialize client's request history if not exists
        if client_id not in self.clients:
            self.clients[client_id] = []
        
        # Filter out old requests
        self.clients[client_id] = [
            timestamp for timestamp in self.clients[client_id]
            if current_time - timestamp < self.window_seconds
        ]
        
        # Check if rate limit exceeded
        if len(self.clients[client_id]) >= self.requests_limit:
            return True
        
        # Add current request timestamp
        self.clients[client_id].append(current_time)
        return False

# Create rate limiter instance
rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW)

# Rate limiter dependency
async def check_rate_limit(request: Request):
    client_id = request.client.host
    if rate_limiter.is_rate_limited(client_id):
        logger.warning(f"Rate limit exceeded for client {client_id}")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds allowed."
        )

# 初始化 PaddleOCR 讀取器
try:
    ocr = PaddleOCR(use_angle_cls=True, lang="en")  # 可換 "ch" 以支援中文
    logger.info("PaddleOCR initialized successfully!")
except Exception as e:
    logger.error(f"Error initializing PaddleOCR: {str(e)}")
    logger.error(traceback.format_exc())
    ocr = None

# URL 正則表達式
URL_REGEX = r"https?://[a-zA-Z0-9./?=_-]+"

def extract_text(image_bytes):
    """使用 PaddleOCR 辨識文字"""
    try:
        if ocr is None:
            raise Exception("PaddleOCR not initialized properly")
            
        image = np.array(cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR))
        result = ocr.ocr(image, cls=True)

        texts = []
        for line in result:
            if line:
                for word_info in line:
                    texts.append(word_info[1][0])  # 取得辨識文字

        return " ".join(texts)
    except Exception as e:
        logger.error(f"Error in OCR processing: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Error: {str(e)}"

def extract_urls(text):
    """從 OCR 輸出的文字中提取網址"""
    return re.findall(URL_REGEX, text)

@app.post("/upload/")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    rate_limit: Any = Depends(check_rate_limit)
):
    """API 端點，接收圖片並回傳識別出的文字"""
    start_time = time.time()
    client_ip = request.client.host
    
    logger.info(f"Received request from {client_ip}, file: {file.filename}")
    
    try:
        # Check file size
        file_size = 0
        contents = BytesIO()
        
        # Read file in chunks to check size
        chunk_size = 1024 * 1024  # 1MB chunks
        chunk = await file.read(chunk_size)
        while chunk:
            file_size += len(chunk)
            contents.write(chunk)
            
            # Check if file is too large
            if file_size > MAX_FILE_SIZE:
                logger.warning(f"File too large: {file_size} bytes, from {client_ip}")
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size allowed is {MAX_FILE_SIZE / (1024 * 1024):.1f} MB"
                )
            
            chunk = await file.read(chunk_size)
        
        # Reset BytesIO position to start
        contents.seek(0)
        image_bytes = contents.read()
        
        # Process image
        text = extract_text(image_bytes)
        logger.info(f"OCR Text length: {len(text)}, from {client_ip}")
        
        # Extract URLs if any
        urls = extract_urls(text)
        logger.info(f"Found {len(urls)} URLs, from {client_ip}")
        
        # Calculate processing time
        process_time = time.time() - start_time
        logger.info(f"Request processed in {process_time:.2f} seconds, from {client_ip}")
        
        return {
            "text": text, 
            "urls": urls,
            "file_size": file_size,
            "process_time": process_time
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.error(f"Error in upload: {str(e)}, from {client_ip}")
        logger.error(error_detail)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if ocr is None:
        raise HTTPException(status_code=500, detail="PaddleOCR not initialized properly")
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024),
        "rate_limit_requests": RATE_LIMIT_REQUESTS,
        "rate_limit_window_seconds": RATE_LIMIT_WINDOW
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "PaddleOCR API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "API information"},
            {"path": "/health", "method": "GET", "description": "Health check endpoint"},
            {"path": "/upload/", "method": "POST", "description": "Upload and process image"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    # Change host to "0.0.0.0" to make it accessible from other machines
    uvicorn.run(app, host="0.0.0.0", port=8000)
