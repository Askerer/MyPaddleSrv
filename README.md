# PaddleOCR React Application

This is a web application that allows users to upload images and perform OCR (Optical Character Recognition) using PaddleOCR.

## Features

- Upload images through a React front-end
- Process images using PaddleOCR in the back-end
- Display OCR results with confidence scores

## Technology Stack

- **Front-end**: React.js
- **Back-end**: FastAPI (Python)
- **OCR Engine**: PaddleOCR

## Prerequisites

Before running the application, make sure you have the following installed:

- Node.js and npm
- Python 3.7+
- PaddlePaddle
- PaddleOCR

## Installation

### Install PaddlePaddle and PaddleOCR

```bash
pip install paddlepaddle
pip install paddleocr
```

### Install Front-end Dependencies

```bash
cd ocr-frontend
npm install
```

## Running the Application

You can start both the front-end and back-end using the `start_app.bat` script:

```bash
./start_app.bat
```

Alternatively, you can start them individually:

### Start the FastAPI Back-end

```bash
python -m uvicorn main:app --reload
```

### Start the React Front-end

```bash
cd ocr-frontend
npm start
```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Upload an image by clicking on the "Choose File" button
3. Click the "Upload and Analyze" button to process the image
4. View the OCR results displayed on the page

## API Endpoints

- `POST /upload/`: Upload an image for OCR processing
- `GET /health`: Check if the backend API is healthy and PaddleOCR is initialized

## Troubleshooting

### 500 Internal Server Error

If you encounter a 500 Internal Server Error when uploading an image, check the following:

1. **PaddleOCR Installation**: Make sure PaddlePaddle and PaddleOCR are properly installed.
   ```bash
   pip install --upgrade paddlepaddle
   pip install --upgrade paddleocr
   ```

2. **Image Format**: Ensure the image format is supported by PaddleOCR. Common formats like PNG, JPG, and JPEG should work.

3. **Check Server Logs**: Look at the terminal running the FastAPI server for detailed error messages.

4. **Dependencies**: Make sure all required dependencies are installed:
   ```bash
   pip install fastapi uvicorn python-multipart Pillow
   ```

### No Response from Server

If the frontend displays "No response from server," check:

1. **Backend Running**: Confirm the FastAPI backend is running on http://localhost:8000.

2. **CORS Issues**: Make sure the CORS settings in `main.py` include your frontend origin.

3. **Network Issues**: Check for any firewall or network issues blocking the connection.

### OCR Results Not Showing Correctly

If OCR results are not displaying properly:

1. **Image Quality**: Use clear, high-resolution images for better OCR accuracy.

2. **Language Support**: Make sure the language parameter in PaddleOCR initialization matches your text language.

3. **Check Console Errors**: Look at the browser's developer console for any JavaScript errors. 