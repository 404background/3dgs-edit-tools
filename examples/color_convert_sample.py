#!/usr/bin/env python3
"""
Simple script to change 3D Gaussian Splatting PLY colors to black

All generated files will be saved in the 'converted' folder.

Usage:
    python color_convert_sample.py [--input_ply INPUT_PLY_FILE] [--color COLOR]
"""

import os
import sys
import csv
import argparse
import numpy as np

# Add the source code directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the library
from src import convert_3dgs_to_csv, convert_csv_to_3dgs
from src.color_utils import detect_color_properties, convert_standard_to_sh_color, SH_COLOR_PROPERTIES


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="3D Gaussian Splatting color conversion sample")
    parser.add_argument("--input_ply", default="Haniwa.ply", help="Input 3D Gaussian Splatting PLY file")
    parser.add_argument("--color", default="black", help="Target color (black, white, red, green, blue, yellow, cyan, magenta)")
    args = parser.parse_args()
    
    # Available color options
    color_options = {
        "black": [0.0, 0.0, 0.0],
        "white": [1.0, 1.0, 1.0],
        "red": [1.0, 0.0, 0.0],
        "green": [0.0, 1.0, 0.0],
        "blue": [0.0, 0.0, 1.0],
        "yellow": [1.0, 1.0, 0.0],
        "cyan": [0.0, 1.0, 1.0],
        "magenta": [1.0, 0.0, 1.0]
    }
    
    # Check if the requested color is valid
    if args.color not in color_options:
        print(f"Error: Unsupported color '{args.color}'. Available options: {', '.join(color_options.keys())}")
        return
    
    target_rgb_color = color_options[args.color]
    
    # Sample file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_ply = os.path.join(current_dir, args.input_ply)
    
    # Extract filename without extension for output file naming
    input_filename = os.path.basename(args.input_ply)
    input_base = os.path.splitext(input_filename)[0]
    
    # Check if the input file exists
    if not os.path.exists(input_ply):
        print(f"Error: Input file not found: {input_ply}")
        return
    
    # Check and create the converted directory
    converted_dir = os.path.join(current_dir, 'converted')
    if not os.path.exists(converted_dir):
        os.makedirs(converted_dir)
        print(f"Created 'converted' directory: {converted_dir}")
    
    print(f"Processing {input_filename}: {input_ply}")
    
    # Convert PLY file to CSV
    csv_path = os.path.join(converted_dir, f"{input_base}.csv")
    csv_path, _ = convert_3dgs_to_csv(input_ply, csv_path)
    print(f"Converted to CSV: {csv_path}")
    
    # Read the CSV file
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        data = [row for row in reader]
    
    # Find color-related attribute indices using color_utils
    is_sh_color = False
    r_idx, g_idx, b_idx, is_sh_color = detect_color_properties(header)
    
    color_indices = []
    if is_sh_color:
        print(f"Detected SH color format (spherical harmonic coefficients)")
        color_indices = [header.index(prop) for prop in SH_COLOR_PROPERTIES if prop in header]
    else:
        if r_idx is not None and g_idx is not None and b_idx is not None:
            color_indices = [r_idx, g_idx, b_idx]
            print(f"Detected standard RGB color format")
        else:
            print("No color-related attributes found.")
            return
    
    if color_indices:
        print(f"Found color-related attributes: {[header[i] for i in color_indices]}")
    else:
        print("No color-related attributes found.")
        return
    
    # Set the path for the modified file
    modified_csv_path = os.path.join(converted_dir, f"{input_base}_{args.color}.csv")
    
    # Convert target RGB color to SH color format if needed
    if is_sh_color:
        # Analyze existing data to determine SH color range
        all_sh_values = []
        for row in data:
            for i in color_indices:
                all_sh_values.append(float(row[i]))
        
        min_val = min(all_sh_values)
        max_val = max(all_sh_values)
        print(f"Original SH color range: {min_val} to {max_val}")
        
        # Convert standard RGB to SH using the detected range
        target_sh_color = convert_standard_to_sh_color(np.array([target_rgb_color]), min_val, max_val)[0]
        print(f"Converting {args.color} RGB {target_rgb_color} to SH color: {target_sh_color}")
        target_color_values = [str(val) for val in target_sh_color]
    else:
        # For standard RGB format
        target_color_values = [str(val) for val in target_rgb_color]
    
    # Modify CSV data
    print(f"\n=== Editing data ===")
    print(f"- Changing all colors to {args.color}...")
    
    with open(modified_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        for row in data:
            # Change color values to target color
            for i, idx in enumerate(color_indices):
                if i < len(target_color_values):
                    row[idx] = target_color_values[i]
            
            writer.writerow(row)
    
    print(f"Saved modified CSV: {modified_csv_path}")
    
    # Convert edited CSV back to PLY
    output_ply = os.path.join(converted_dir, f"{input_base}_{args.color}.ply")
    restored_ply = convert_csv_to_3dgs(modified_csv_path, None, output_ply)
    print(f"\nConverted modified data to PLY: {restored_ply}")
    
    print("\n=== Conversion summary ===")
    print(f"Original PLY file: {input_ply}")
    print(f"Intermediate CSV file: {csv_path}")
    print(f"Modified CSV file ({args.color}): {modified_csv_path}")
    print(f"Final PLY file: {restored_ply}")
    print(f"\nAll output files were saved in {converted_dir}")
    print(f"\nPlease compare the original PLY file with the {args.color} PLY file.")


if __name__ == "__main__":
    main()
