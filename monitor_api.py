import time
import requests
import datetime
import argparse
import os
import csv
import signal
import sys

# API endpoint
API_URL = "http://localhost:8000/upload/"

# Global flag for stopping the monitor
running = True

def signal_handler(sig, frame):
    """Handle ctrl+c to gracefully stop monitoring"""
    global running
    print("\nStopping monitoring...")
    running = False

def monitor_api(image_path, interval=60, output_file="monitoring_results.csv", duration_hours=None):
    """Monitor the API by sending requests at regular intervals"""
    start_time = time.time()
    
    # Check if the file exists to determine if we need to write the header
    file_exists = os.path.isfile(output_file)
    
    with open(output_file, 'a', newline='') as csv_file:
        fieldnames = ['timestamp', 'response_time', 'status', 'status_code', 'error_message']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # Write header if the file is new
        if not file_exists:
            writer.writeheader()
        
        print(f"Starting API monitoring, sending requests every {interval} seconds")
        print(f"Press Ctrl+C to stop monitoring")
        print(f"Results are being saved to {output_file}")
        
        if duration_hours:
            end_time = start_time + (duration_hours * 3600)
            print(f"Monitoring will automatically stop after {duration_hours} hours")
        else:
            end_time = float('inf')
        
        # Monitor loop
        while running and time.time() < end_time:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                with open(image_path, "rb") as image_file:
                    files = {"file": (os.path.basename(image_path), image_file, "image/jpeg")}
                    
                    # Measure response time
                    request_start = time.time()
                    response = requests.post(API_URL, files=files, timeout=30)
                    request_end = time.time()
                    response_time = request_end - request_start
                    
                    # Prepare results
                    result = {
                        'timestamp': timestamp,
                        'response_time': response_time,
                        'status': 'success' if response.status_code == 200 else 'error',
                        'status_code': response.status_code,
                        'error_message': ''
                    }
                    
                    if response.status_code != 200:
                        result['error_message'] = response.text[:100]
                    
                    # Write results
                    writer.writerow(result)
                    csv_file.flush()  # Ensure data is written immediately
                    
                    # Print status
                    status_emoji = "✅" if response.status_code == 200 else "❌"
                    print(f"{timestamp} - {status_emoji} Response time: {response_time:.2f}s, Status: {response.status_code}")
                    
            except Exception as e:
                # Handle request errors
                result = {
                    'timestamp': timestamp,
                    'response_time': -1,
                    'status': 'exception',
                    'status_code': 0,
                    'error_message': str(e)[:100]
                }
                
                writer.writerow(result)
                csv_file.flush()
                print(f"{timestamp} - ❌ Error: {str(e)}")
            
            # Wait for the next interval if we're still supposed to be monitoring
            if running and time.time() < end_time:
                remaining_sleep = max(0, interval - (time.time() - request_start))
                time.sleep(remaining_sleep)
        
        # Final summary
        elapsed = time.time() - start_time
        print(f"\nMonitoring completed after {elapsed/60:.1f} minutes")

def main():
    parser = argparse.ArgumentParser(description="Monitor PaddleOCR API over time")
    parser.add_argument("--image", type=str, required=True, help="Path to test image")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between requests")
    parser.add_argument("--output", type=str, default="monitoring_results.csv", help="Output CSV file")
    parser.add_argument("--duration", type=float, help="Duration in hours (optional)")
    
    args = parser.parse_args()
    
    # Set up signal handling for graceful termination
    signal.signal(signal.SIGINT, signal_handler)
    
    monitor_api(args.image, args.interval, args.output, args.duration)

if __name__ == "__main__":
    main() 