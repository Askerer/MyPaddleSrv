@echo off
echo Starting PaddleOCR Application...

rem Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    goto :eof
)

rem Check if Node.js is installed
node --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH.
    goto :eof
)

rem Check if required Python packages are installed
python -c "import paddleocr" > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PaddleOCR is not installed. Please run: pip install paddleocr paddlepaddle
    goto :eof
)

python -c "import fastapi" > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: FastAPI is not installed. Please run: pip install fastapi uvicorn python-multipart
    goto :eof
)

rem Check if npm packages are installed for the React app
if not exist "ocr-frontend\node_modules" (
    echo Installing React dependencies...
    cd ocr-frontend
    npm install
    cd ..
)

echo Starting FastAPI Backend...
start cmd /k "python -m uvicorn main:app --reload"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo Starting React Frontend...
cd ocr-frontend
start cmd /k "npm start"

echo Application started!
echo Backend is running on http://localhost:8000
echo Frontend is running on http://localhost:3000
echo.
echo If you encounter any issues:
echo 1. Check if PaddlePaddle and PaddleOCR are properly installed
echo 2. Check the server logs for any errors
echo 3. Verify the image format is supported by PaddleOCR 