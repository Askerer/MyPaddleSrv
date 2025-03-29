import time
import requests
import concurrent.futures
import statistics
import os
import argparse
from pathlib import Path

# API endpoint
API_URL = "http://localhost:8000/upload/"

def upload_image(image_path):
    """Upload a single image and measure response time"""
    start_time = time.time()
    try:
        with open(image_path, "rb") as image_file:
            files = {"file": (os.path.basename(image_path), image_file, "image/jpeg")}
            response = requests.post(API_URL, files=files)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            return {
                "status": "success",
                "response_time": response_time,
                "text_length": len(response.json().get("text", "")),
                "status_code": response.status_code
            }
        else:
            return {
                "status": "error",
                "response_time": response_time,
                "error": response.text,
                "status_code": response.status_code
            }
    except Exception as e:
        end_time = time.time()
        return {
            "status": "exception",
            "response_time": end_time - start_time,
            "error": str(e),
            "status_code": 0
        }

def concurrent_test(image_path, num_requests, num_workers):
    """Test API with concurrent requests"""
    print(f"Starting concurrent test with {num_requests} requests using {num_workers} workers")
    print(f"Testing image: {image_path}")
    
    results = []
    start_time = time.time()
    
    # Use a thread pool to make concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit all tasks
        futures = [executor.submit(upload_image, image_path) for _ in range(num_requests)]
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            completed = len(results)
            if completed % 5 == 0 or completed == num_requests:
                print(f"Completed {completed}/{num_requests} requests")
    
    end_time = time.time()
    
    # Analyze results
    total_time = end_time - start_time
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = len(results) - success_count
    
    response_times = [r["response_time"] for r in results if r["status"] == "success"]
    
    if response_times:
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
    else:
        avg_response_time = min_response_time = max_response_time = p95_response_time = 0
    
    # Print summary
    print("\n===== TEST RESULTS =====")
    print(f"Total requests: {num_requests}")
    print(f"Concurrent workers: {num_workers}")
    print(f"Successful requests: {success_count} ({success_count/num_requests*100:.2f}%)")
    print(f"Failed requests: {error_count} ({error_count/num_requests*100:.2f}%)")
    print(f"Total test time: {total_time:.2f} seconds")
    print(f"Request throughput: {num_requests/total_time:.2f} requests/second")
    
    if response_times:
        print("\nResponse times (successful requests):")
        print(f"  Average: {avg_response_time:.2f} seconds")
        print(f"  Minimum: {min_response_time:.2f} seconds")
        print(f"  Maximum: {max_response_time:.2f} seconds")
        print(f"  95th percentile: {p95_response_time:.2f} seconds")
    
    # Print some error details if there were errors
    if error_count > 0:
        print("\nSample errors:")
        for r in [r for r in results if r["status"] != "success"][:5]:  # Show up to 5 errors
            print(f"  Status code: {r['status_code']}, Error: {r.get('error', 'Unknown error')[:100]}...")
    
    return results

def test_file_size_limits(directory, num_tests=3):
    """Test API with different file sizes"""
    print("\n===== FILE SIZE LIMIT TEST =====")
    files = list(Path(directory).glob("*.jpg")) + list(Path(directory).glob("*.png")) + list(Path(directory).glob("*.jpeg"))
    
    if not files:
        print(f"No image files found in {directory}")
        return
    
    # Sort files by size
    files_with_size = [(f, f.stat().st_size) for f in files]
    files_with_size.sort(key=lambda x: x[1])
    
    print(f"Testing {min(num_tests, len(files_with_size))} files of different sizes")
    
    # Test a sample of files with different sizes
    test_files = []
    if len(files_with_size) <= num_tests:
        test_files = files_with_size
    else:
        # Select files distributed across the size range
        step = len(files_with_size) // num_tests
        for i in range(0, len(files_with_size), step):
            if len(test_files) < num_tests:
                test_files.append(files_with_size[i])
    
    results = []
    for file_path, size in test_files:
        size_kb = size / 1024
        print(f"\nTesting file: {file_path.name} ({size_kb:.2f} KB)")
        result = upload_image(str(file_path))
        results.append((file_path, size, result))
        
        status = "✅ Success" if result["status"] == "success" else f"❌ Failed: {result.get('error', 'Unknown error')[:50]}..."
        print(f"  Result: {status}")
        print(f"  Response time: {result['response_time']:.2f} seconds")
        
        # Add a small delay between tests
        time.sleep(1)
    
    # Print summary
    print("\nFile Size Test Summary:")
    print("| File | Size (KB) | Status | Response Time (s) |")
    print("|------|-----------|--------|-------------------|")
    for file_path, size, result in results:
        size_kb = size / 1024
        status = "Success" if result["status"] == "success" else "Failed"
        print(f"| {file_path.name} | {size_kb:.2f} | {status} | {result['response_time']:.2f} |")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Test PaddleOCR API performance")
    parser.add_argument("--image", type=str, help="Path to test image", default="test.jpg")
    parser.add_argument("--requests", type=int, help="Number of requests to make", default=20)
    parser.add_argument("--workers", type=int, help="Number of concurrent workers", default=5)
    parser.add_argument("--test-size-limits", action="store_true", help="Test size limits with multiple files")
    parser.add_argument("--image-dir", type=str, help="Directory containing test images", default="./test_images")
    
    args = parser.parse_args()
    
    if args.test_size_limits:
        test_file_size_limits(args.image_dir)
    else:
        concurrent_test(args.image, args.requests, args.workers)

if __name__ == "__main__":
    main() 