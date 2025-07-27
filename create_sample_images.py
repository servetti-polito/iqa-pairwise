#!/usr/bin/env python3
"""
Script to create sample placeholder images for testing the image comparison application.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_image(text, filename, size=(800, 600), bg_color='lightblue', text_color='darkblue'):
    """Create a simple placeholder image with text"""
    # Create image
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fall back to default if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    # Get text size and position it in center
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill=text_color, font=font)
    
    # Save image
    img.save(filename)
    print(f"Created: {filename}")

def main():
    # Create static/images directory if it doesn't exist
    images_dir = "static/images"
    os.makedirs(images_dir, exist_ok=True)
    
    # Create sample images
    sample_images = [
        ("Image 1 Left", "image1_left.jpg", 'lightcoral', 'darkred'),
        ("Image 1 Right", "image1_right.jpg", 'lightgreen', 'darkgreen'),
        ("Image 2 Left", "image2_left.jpg", 'lightblue', 'darkblue'),
        ("Image 2 Right", "image2_right.jpg", 'lightyellow', 'orange'),
        ("Image 3 Left", "image3_left.jpg", 'lightpink', 'purple'),
        ("Image 3 Right", "image3_right.jpg", 'lightgray', 'black'),
        ("Image 4 Left", "image4_left.jpg", 'lightcyan', 'teal'),
        ("Image 4 Right", "image4_right.jpg", 'lavender', 'indigo'),
        ("Image 5 Left", "image5_left.jpg", 'wheat', 'brown'),
        ("Image 5 Right", "image5_right.jpg", 'lightseagreen', 'darkslategray')
    ]
    
    for text, filename, bg_color, text_color in sample_images:
        filepath = os.path.join(images_dir, filename)
        create_sample_image(text, filepath, bg_color=bg_color, text_color=text_color)
    
    print(f"\nCreated {len(sample_images)} sample images in {images_dir}/")
    print("You can now run the Flask application with: python app.py")

if __name__ == "__main__":
    main()
