@echo off
echo PaddleOCR API Testing Suite
echo =======================

REM Create test directory if it doesn't exist
if not exist "test_images" mkdir test_images

REM Check if we need to generate test images
set /p gen_images="Generate test images? (y/n): "
if /i "%gen_images%"=="y" (
    echo Generating test images...
    python generate_test_images.py --count 15
)

echo.
echo Running API tests...
echo.

REM Test for different scenarios
set /p test_type="Select test type (1=Concurrency, 2=Size Limits, 3=Both): "

if "%test_type%"=="1" (
    REM Concurrency test with first test image
    echo Running concurrency test...
    python test_api_performance.py --image "test_images\test_image_1.jpg" --requests 20 --workers 5
) else if "%test_type%"=="2" (
    REM Size limits test
    echo Running size limits test...
    python test_api_performance.py --test-size-limits --image-dir "test_images"
) else if "%test_type%"=="3" (
    REM Both tests
    echo Running concurrency test...
    python test_api_performance.py --image "test_images\test_image_1.jpg" --requests 20 --workers 5
    
    echo.
    echo Running size limits test...
    python test_api_performance.py --test-size-limits --image-dir "test_images"
) else (
    echo Invalid selection
)

echo.
echo API testing complete
pause 