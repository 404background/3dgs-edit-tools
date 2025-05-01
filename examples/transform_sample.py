#!/usr/bin/env python3
"""
Coordinate transformation sample for 3D Gaussian Splatting PLY files

This sample performs the following operations:
1. Convert PLY file to CSV format
2. Transform 3D coordinates (scaling, rotation, translation, etc.)
3. Convert the transformed CSV data back to PLY format

All output files are saved in the converted folder.

Usage:
    python transform_sample.py [--input_ply INPUT_PLY_FILE]
"""

import os
import sys
import csv
import math
import numpy as np
import argparse

# Add the source code directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the library
from src import convert_3dgs_to_csv, convert_csv_to_3dgs


def rotate_z(x, y, angle_deg):
    """Apply rotation around Z axis"""
    angle_rad = math.radians(angle_deg)
    cos_val = math.cos(angle_rad)
    sin_val = math.sin(angle_rad)
    new_x = x * cos_val - y * sin_val
    new_y = x * sin_val + y * cos_val
    return new_x, new_y


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="3D Gaussian Splatting coordinate transformation sample")
    parser.add_argument("--input_ply", default="Haniwa.ply", help="Input 3D Gaussian Splatting PLY file")
    args = parser.parse_args()
    
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
    
    print(f"Performing coordinate transformation for {input_filename}: {input_ply}")
    
    # Convert PLY file to CSV
    csv_path = os.path.join(converted_dir, f"{input_base}.csv")
    csv_path, _ = convert_3dgs_to_csv(input_ply, csv_path)
    print(f"Converted to CSV: {csv_path}")
    
    # Read the CSV file
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        data = [row for row in reader]
    
    # Find X, Y, Z coordinate indices (typically the first 3 columns)
    coord_indices = []
    for i, attr in enumerate(header[:10]):  # Search only the first 10 columns
        if attr == 'x' or attr == 'y' or attr == 'z' or attr == 'pos_0' or attr == 'pos_1' or attr == 'pos_2':
            coord_indices.append((i, attr))
    
    if len(coord_indices) >= 3:
        print(f"Found coordinate attributes: {coord_indices}")
        x_idx, y_idx, z_idx = [idx for idx, _ in coord_indices[:3]]
    else:
        print("Coordinate attributes not found. Using the first 3 columns as default.")
        x_idx, y_idx, z_idx = 0, 1, 2
    
    # Scale: double the width
    scale_factor_x = 2.0
    # Rotation: 45 degrees around Z axis
    rotation_angle = 45

    # Set the path for the modified file
    transformed_csv_path = os.path.join(converted_dir, f"{input_base}_transformed.csv")
    
    print("\n=== Transforming data ===")
    print(f"- X-axis: {scale_factor_x}x scale")
    print(f"- Z-axis rotation: {rotation_angle} degrees")
    
    # Transform the data
    with open(transformed_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        for row in data:
            # Get coordinates
            x = float(row[x_idx])
            y = float(row[y_idx])
            # z = float(row[z_idx])  # Z coordinate is not modified
            
            # Apply scaling
            x *= scale_factor_x
            
            # Apply rotation
            x, y = rotate_z(x, y, rotation_angle)
            
            # Update coordinates
            row[x_idx] = str(x)
            row[y_idx] = str(y)
            
            writer.writerow(row)
    
    print(f"Saved transformed CSV: {transformed_csv_path}")
    
    # Convert the transformed CSV back to PLY
    output_ply = os.path.join(converted_dir, f"{input_base}_transformed.ply")
    restored_ply = convert_csv_to_3dgs(transformed_csv_path, None, output_ply)
    print(f"\nConverted transformed data to PLY: {restored_ply}")
    
    print("\n=== Transformation summary ===")
    print(f"Original PLY file: {input_ply}")
    print(f"Intermediate CSV file: {csv_path}")
    print(f"Transformed CSV file: {transformed_csv_path}")
    print(f"Final PLY file: {restored_ply}")
    print(f"\nAll output files were saved in {converted_dir}")
    print("\nPlease compare the original PLY file with the transformed PLY file in a 3D viewer.")
    print("The width should be doubled and rotated 45 degrees around the Z axis.")


if __name__ == "__main__":
    main()
