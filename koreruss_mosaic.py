#!/usr/bin/env python3
"""
Photo Mosaic Generator for "KORERUSSBIZ"
- Scans a folder for images (.jpg, .png)
- Creates tiles (small squares) from each image
- Builds a mosaic that spells "KORERUSSBIZ"
"""

import os
import sys
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_target_text(size=(3000, 600), text="KORERUSSBIZ"):
    """Create a target image with white text on black background."""
    img = Image.new('RGB', size, color='black')
    try:
        # Try to use a nice font (if available)
        font = ImageFont.truetype("/system/fonts/DroidSans.ttf", 300)
    except:
        # Fallback to default
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    # Calculate text position to center
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    draw.text((x, y), text, font=font, fill='white')
    return img

def load_images(image_folder, tile_size=(100, 100)):
    """Load images, resize to tiles, and store average colors."""
    tiles = []
    colors = []
    valid_ext = ('.jpg', '.jpeg', '.png', '.bmp')
    for f in Path(image_folder).iterdir():
        if f.suffix.lower() in valid_ext:
            try:
                img = Image.open(f).convert('RGB')
                img = img.resize(tile_size, Image.Resampling.LANCZOS)
                tiles.append(img)
                # Compute average color (as numpy array)
                avg = np.array(img).mean(axis=(0,1))
                colors.append(avg)
            except Exception as e:
                print(f"Skipping {f.name}: {e}")
    return tiles, np.array(colors)

def match_tiles_to_target(target_img, tiles, tile_colors, tile_size=(100,100)):
    """
    For each tile region in the target, select the tile with closest average color.
    Returns a mosaic image.
    """
    target_arr = np.array(target_img)
    h, w = target_arr.shape[:2]
    tile_h, tile_w = tile_size

    rows = h // tile_h
    cols = w // tile_w

    # Crop target to exact multiple of tile size
    target_crop = target_arr[:rows*tile_h, :cols*tile_w]

    mosaic = Image.new('RGB', (cols*tile_w, rows*tile_h))
    for i in range(rows):
        for j in range(cols):
            region = target_crop[i*tile_h:(i+1)*tile_h, j*tile_w:(j+1)*tile_w]
            avg_color = region.mean(axis=(0,1))
            dist = np.linalg.norm(tile_colors - avg_color, axis=1)
            best_idx = np.argmin(dist)
            mosaic.paste(tiles[best_idx], (j*tile_w, i*tile_h))
    return mosaic

def main():
    parser = argparse.ArgumentParser(description="Create photo mosaic spelling KORERUSSBIZ")
    parser.add_argument("image_folder", help="Folder containing source images")
    parser.add_argument("--output", default="mosaic.png", help="Output filename")
    parser.add_argument("--tile", type=int, default=50, help="Tile size in pixels (default 50)")
    parser.add_argument("--width", type=int, default=2000, help="Target image width (default 2000)")
    parser.add_argument("--height", type=int, default=400, help="Target image height (default 400)")
    args = parser.parse_args()

    print("Loading images...")
    tile_size = (args.tile, args.tile)
    tiles, colors = load_images(args.image_folder, tile_size)
    if len(tiles) == 0:
        print("No images found in folder.")
        return
    print(f"Loaded {len(tiles)} images.")

    print("Creating target text image...")
    target = create_target_text(size=(args.width, args.height), text="KORERUSSBIZ")

    print("Matching tiles to target...")
    mosaic = match_tiles_to_target(target, tiles, colors, tile_size)

    print(f"Saving mosaic to {args.output}...")
    mosaic.save(args.output)
    print("Done!")

if __name__ == "__main__":
    main()
