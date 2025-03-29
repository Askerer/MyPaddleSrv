# PaddleOCR API Testing Tools

This set of scripts helps you test the performance, limits, and stability of your PaddleOCR API service.

## Requirements

Before using these tools, make sure you have the required Python packages:

```bash
pip install requests pillow argparse
```

## Tools Included

### 1. Test Image Generator (`generate_test_images.py`)

This script generates a variety of test images with different sizes and content for testing purposes.

**Usage:**

```bash
python generate_test_images.py --output-dir ./test_images --count 15
```

**Parameters:**
- `--output-dir`: Directory to save test images (default: ./test_images)
- `--count`: Number of test images to generate (default: 10)

### 2. API Performance Tester (`test_api_performance.py`)

This script tests the performance of your OCR API under different scenarios.

**Usage:**

```bash
# Concurrency test
python test_api_performance.py --image test_images/test_image_1.jpg --requests 20 --workers 5

# Size limits test
python test_api_performance.py --test-size-limits --image-dir test_images
```

**Parameters:**
- `--image`: Path to test image for concurrency testing
- `--requests`: Number of requests to make in the concurrency test
- `--workers`: Number of concurrent workers (simulates multiple users)
- `--test-size-limits`: Run the file size limit test
- `--image-dir`: Directory containing test images for size testing

### 3. Long-term API Monitor (`monitor_api.py`)

This script monitors your API over a long period of time to check stability and response times.

**Usage:**

```bash
python monitor_api.py --image test_images/test_image_1.jpg --interval 60 --output results.csv --duration 24
```

**Parameters:**
- `--image`: Path to test image
- `--interval`: Seconds between requests (default: 60)
- `--output`: Output CSV file for results (default: monitoring_results.csv)
- `--duration`: Duration in hours (optional, runs indefinitely if not specified)

### 4. Batch Runner (`run_api_tests.bat`)

A Windows batch script that provides an interactive menu to run the various tests.

**Usage:**

Simply run the batch file and follow the prompts:

```bash
run_api_tests.bat
```

## Testing Methodology

### Concurrency Testing

The concurrency test simulates multiple users accessing your API simultaneously. It helps you understand:

- How many concurrent requests your API can handle
- Response time degradation under load
- Error rates when the system is under pressure

### Size Limit Testing

This test helps determine:

- Maximum file size your API can handle
- How response time varies with image size
- Any file size thresholds where errors become more common

### Long-term Stability Monitoring

The monitoring tool helps you understand:

- Long-term stability of your service
- Response time variations over time
- Patterns of failures or degraded performance

## Interpreting Results

### Response Time Metrics

- **Average**: Typical response time
- **Minimum**: Best-case response time
- **Maximum**: Worst-case response time
- **95th Percentile**: Response time that 95% of requests fall under, ignoring outliers

### Success Rates

Pay attention to success rates under different conditions. Consider adjusting your API configuration if:

- Success rate drops below 99% during normal load
- Response times increase dramatically with concurrent users
- Certain file sizes consistently cause failures

### Common Issues and Solutions

1. **High error rates with concurrent requests**:
   - Increase server resources
   - Implement rate limiting
   - Add a request queue

2. **Failures with large images**:
   - Set maximum file size limits
   - Implement automatic image resizing
   - Increase timeout settings

3. **Degrading performance over time**:
   - Check for memory leaks
   - Implement server auto-restart
   - Add load balancing

## Customizing the Tests

You can modify the scripts to:

- Test different endpoints
- Change timeout settings
- Adjust test parameters
- Add custom test metrics

Edit the API_URL variable in the scripts to point to your specific API endpoint. 