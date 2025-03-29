from PIL import Image, ImageDraw, ImageFont
import os
import random
import string
import argparse

def create_directory(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def generate_random_text(length):
    """Generate random text for the image"""
    return ' '.join(''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(3, 10))) 
                   for _ in range(length))

def create_image_with_text(width, height, text, filename, quality=95):
    """Create an image with the specified dimensions containing text"""
    # Create image with white background
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a common font that should be available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        # If the font is not available, use default font
        font = ImageFont.load_default()
    
    # Add some shapes and lines for complexity
    for _ in range(10):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
        draw.line((x1, y1, x2, y2), fill=color, width=2)
    
    # Draw the text
    text_color = (0, 0, 0)  # Black
    
    # Break text into multiple lines
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        # Check if the current line is too long
        test_line = ' '.join(current_line)
        if font.getlength(test_line) > (width - 40):  # Leave a margin
            # If too long, remove the last word and add the line
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # If a single word is too long, keep it and let it be truncated
                lines.append(test_line)
                current_line = []
    
    # Add the last line if there's anything left
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw each line of text
    y_position = 20
    for line in lines:
        draw.text((20, y_position), line, font=font, fill=text_color)
        y_position += 30
    
    # Save the image with the specified quality
    image.save(filename, quality=quality)
    
    return os.path.getsize(filename)

def generate_test_images(output_dir, count=10):
    """Generate a set of test images with varying sizes"""
    create_directory(output_dir)
    
    print(f"Generating {count} test images in {output_dir}")
    
    sizes = []
    
    # Generate images of different sizes
    for i in range(count):
        # Vary the dimensions
        width = random.randint(600, 2400)
        height = random.randint(400, 1600)
        
        # Generate more text for larger images
        text_length = random.randint(20, 100)
        text = generate_random_text(text_length)
        
        # Vary the JPEG quality to get different file sizes
        quality = random.randint(60, 95)
        
        filename = os.path.join(output_dir, f"test_image_{i+1}.jpg")
        file_size = create_image_with_text(width, height, text, filename, quality)
        
        size_kb = file_size / 1024
        print(f"Created: {filename} - {width}x{height} pixels, {size_kb:.2f} KB")
        
        sizes.append((filename, size_kb))
    
    # Print summary
    print("\nGenerated test images:")
    print("| Filename | Size (KB) |")
    print("|----------|-----------|")
    for filename, size_kb in sizes:
        print(f"| {os.path.basename(filename)} | {size_kb:.2f} |")

def main():
    parser = argparse.ArgumentParser(description="Generate test images for OCR testing")
    parser.add_argument("--output-dir", type=str, default="./test_images", help="Directory to save test images")
    parser.add_argument("--count", type=int, default=10, help="Number of test images to generate")
    
    args = parser.parse_args()
    generate_test_images(args.output_dir, args.count)

if __name__ == "__main__":
    main() 