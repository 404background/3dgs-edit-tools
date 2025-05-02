#!/usr/bin/env python3
"""
Coordinate transformation sample for 3D Gaussian Splatting PLY files

This sample performs the following operations:
1. Convert PLY file to CSV format
2. Transform 3D coordinates (scaling, rotation, translation, etc.)
3. Convert the transformed CSV data back to PLY format

All output files are saved in the converted folder.

Usage:
    python transform_sample.py [--input_ply INPUT_PLY_FILE] [--rotation-axis AXIS] 
    [--rotation-angle DEGREES] [--translate-x X] [--translate-y Y] [--translate-z Z]
    [--scale-x X] [--scale-y Y] [--scale-z Z]
"""

import os
import sys
import csv
import math
import numpy as np
import argparse
from scipy.spatial.transform import Rotation as R

# Add the source code directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the library
from src import convert_3dgs_to_csv, convert_csv_to_3dgs


def rotate_point(x, y, z, angle_deg, axis='z'):
    """Apply rotation around specified axis"""
    angle_rad = math.radians(angle_deg)
    
    if axis == 'z':
        # Rotation around Z axis
        cos_val = math.cos(angle_rad)
        sin_val = math.sin(angle_rad)
        new_x = x * cos_val - y * sin_val
        new_y = x * sin_val + y * cos_val
        new_z = z
    elif axis == 'y':
        # Rotation around Y axis
        cos_val = math.cos(angle_rad)
        sin_val = math.sin(angle_rad)
        new_x = x * cos_val + z * sin_val
        new_y = y
        new_z = -x * sin_val + z * cos_val
    elif axis == 'x':
        # Rotation around X axis
        cos_val = math.cos(angle_rad)
        sin_val = math.sin(angle_rad)
        new_x = x
        new_y = y * cos_val - z * sin_val
        new_z = y * sin_val + z * cos_val
    else:
        # No rotation for unknown axis
        new_x, new_y, new_z = x, y, z
    
    return new_x, new_y, new_z


def rotate_quaternion(quat, angle_deg, axis='z'):
    """
    Apply rotation to an existing quaternion
    
    Args:
        quat: List of 4 values [w, x, y, z] representing the quaternion
        angle_deg: Rotation angle in degrees
        axis: Axis of rotation ('x', 'y', or 'z')
        
    Returns:
        List of 4 values representing the new quaternion
    """
    # Convert input quaternion to scipy Rotation object
    # 3DGS may use [x, y, z, w] format, so reorder if needed
    orig_rotation = R.from_quat([quat[1], quat[2], quat[3], quat[0]])
    
    # Create rotation around specified axis
    angle_rad = math.radians(angle_deg)
    if axis == 'z':
        rotation_matrix = R.from_rotvec([0, 0, angle_rad])
    elif axis == 'y':
        rotation_matrix = R.from_rotvec([0, angle_rad, 0])
    elif axis == 'x':
        rotation_matrix = R.from_rotvec([angle_rad, 0, 0])
    else:
        # No rotation for unknown axis
        return quat
    
    # Apply the rotation
    new_rotation = rotation_matrix * orig_rotation
    
    # Convert back to quaternion in [w, x, y, z] format
    quat_xyzw = new_rotation.as_quat()
    # Return in [w, x, y, z] format
    return [quat_xyzw[3], quat_xyzw[0], quat_xyzw[1], quat_xyzw[2]]


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="3D Gaussian Splatting coordinate transformation sample")
    parser.add_argument("--input_ply", default="Haniwa.ply", help="Input 3D Gaussian Splatting PLY file")
    # Rotation settings
    parser.add_argument("--rotation-axis", choices=['x', 'y', 'z'], default='z', help="Rotation axis (x, y, or z)")
    parser.add_argument("--rotation-angle", type=float, default=45.0, help="Rotation angle in degrees")
    # Scaling settings
    parser.add_argument("--scale-x", type=float, default=2.0, help="Scale factor for X axis")
    parser.add_argument("--scale-y", type=float, default=1.0, help="Scale factor for Y axis")
    parser.add_argument("--scale-z", type=float, default=1.0, help="Scale factor for Z axis")
    # Translation settings
    parser.add_argument("--translate-x", type=float, default=0.0, help="Translation along X axis")
    parser.add_argument("--translate-y", type=float, default=0.0, help="Translation along Y axis")
    parser.add_argument("--translate-z", type=float, default=0.0, help="Translation along Z axis")
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
        
    # Find quaternion indices (rotation/orientation)
    quat_indices = []
    for i, attr in enumerate(header):
        if attr == 'rot_0' or attr == 'rot_1' or attr == 'rot_2' or attr == 'rot_3' or attr == 'rotation_0' or attr == 'rotation_1' or attr == 'rotation_2' or attr == 'rotation_3':
            quat_indices.append((i, attr))
    
    if len(quat_indices) >= 4:
        print(f"Found quaternion attributes: {quat_indices}")
        q_w_idx, q_x_idx, q_y_idx, q_z_idx = [idx for idx, _ in quat_indices[:4]]
        has_quaternions = True
    else:
        print("Quaternion attributes not found. Only position will be transformed.")
        has_quaternions = False
    
    # Get transformation parameters
    rotation_axis = args.rotation_axis
    rotation_angle = args.rotation_angle
    scale_x = args.scale_x
    scale_y = args.scale_y
    scale_z = args.scale_z
    translate_x = args.translate_x
    translate_y = args.translate_y
    translate_z = args.translate_z

    # Set the path for the modified file
    transformed_csv_path = os.path.join(converted_dir, f"{input_base}_transformed.csv")
    
    print("\n=== Transforming data ===")
    print(f"- Scale: X:{scale_x}x, Y:{scale_y}x, Z:{scale_z}x")
    print(f"- Rotation: {rotation_angle} degrees around {rotation_axis.upper()} axis")
    print(f"- Translation: X:{translate_x}, Y:{translate_y}, Z:{translate_z}")
    if has_quaternions:
        print("- Ellipsoid orientations will also be rotated")
    
    # Transform the data
    with open(transformed_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        for row in data:
            # Get coordinates
            x = float(row[x_idx])
            y = float(row[y_idx])
            z = float(row[z_idx])
            
            # Apply scaling
            x *= scale_x
            y *= scale_y
            z *= scale_z
            
            # Apply rotation to position
            x, y, z = rotate_point(x, y, z, rotation_angle, rotation_axis)
            
            # Apply translation
            x += translate_x
            y += translate_y
            z += translate_z
            
            # Update coordinates
            row[x_idx] = str(x)
            row[y_idx] = str(y)
            row[z_idx] = str(z)
            
            # Apply rotation to quaternion orientation if available
            if has_quaternions:
                try:
                    # Get quaternion values
                    quat = [
                        float(row[q_w_idx]),
                        float(row[q_x_idx]),
                        float(row[q_y_idx]),
                        float(row[q_z_idx])
                    ]
                    
                    # Apply rotation to quaternion
                    new_quat = rotate_quaternion(quat, rotation_angle, rotation_axis)
                    
                    # Update quaternion values
                    row[q_w_idx] = str(new_quat[0])
                    row[q_x_idx] = str(new_quat[1])
                    row[q_y_idx] = str(new_quat[2])
                    row[q_z_idx] = str(new_quat[3])
                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not update quaternion in a row: {e}")
            
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
    transformation_desc = []
    if any([scale_x != 1.0, scale_y != 1.0, scale_z != 1.0]):
        transformation_desc.append(f"Scaling (X:{scale_x}x, Y:{scale_y}x, Z:{scale_z}x)")
    if rotation_angle != 0:
        transformation_desc.append(f"{rotation_angle} degree rotation around {rotation_axis.upper()} axis")
    if any([translate_x != 0, translate_y != 0, translate_z != 0]):
        transformation_desc.append(f"Translation (X:{translate_x}, Y:{translate_y}, Z:{translate_z})")
    print(f"Applied transformations: {', '.join(transformation_desc)}")
    print("Ellipsoid orientations are correctly rotated as well.")


if __name__ == "__main__":
    main()
