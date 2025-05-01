"""
Sample script demonstrating how to convert between 3D Gaussian Splatting and point cloud formats.
This workflow allows for editing the data in external tools and then restoring
it back to 3D Gaussian Splatting format with all the additional metadata preserved.

The script uses CSV format as an intermediate step for easier editing.
"""

import os
import sys
import numpy as np
import argparse

# Add the parent directory to the path to import the src package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import convert_3dgs_to_pointcloud, convert_pointcloud_to_3dgs
from src.pointcloud_to_csv import convert_pointcloud_to_csv, convert_csv_to_pointcloud


def main():
    """
    Demonstrates a simplified workflow:
    1. Convert 3DGS to point cloud
    2. Convert point cloud to CSV for editing
    3. Edit the CSV data (simulate by changing colors)
    4. Convert CSV back to point cloud
    5. Convert point cloud back to 3DGS format
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Convert 3D Gaussian Splatting to editable formats and back")
    parser.add_argument("--input_ply", default="Haniwa.ply", help="Input 3D Gaussian Splatting PLY file")
    args = parser.parse_args()
    
    # Get current directory for correct path resolution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths with correct path joining
    input_3dgs_file = os.path.join(current_dir, args.input_ply)
    
    # Extract filename without extension for output file naming
    input_filename = os.path.basename(args.input_ply)
    input_base = os.path.splitext(input_filename)[0]
    
    # Make sure the converted directory exists
    converted_dir = os.path.join(current_dir, "converted")
    os.makedirs(converted_dir, exist_ok=True)
    
    # Define simplified file paths for the workflow
    pointcloud_file = os.path.join(converted_dir, f"{input_base}_pointcloud.ply")
    pointcloud_csv_file = os.path.join(converted_dir, f"{input_base}_pointcloud.csv")  # Changed to _pointcloud.csv
    edited_pointcloud_file = os.path.join(converted_dir, f"{input_base}_from_csv.ply")
    output_3dgs_file = os.path.join(converted_dir, f"{input_base}_from_pointcloud.ply")

    # STREAMLINED WORKFLOW
    print(f"\n=== 3D GAUSSIAN SPLATTING EDITING WORKFLOW ===")
    
    # Step 1: Convert 3DGS to point cloud
    print(f"\n1. Converting 3D Gaussian Splatting to point cloud...")
    pointcloud_path = convert_3dgs_to_pointcloud(input_3dgs_file, pointcloud_file)
    print(f"   Point cloud saved to {pointcloud_path}")
    
    # Step 2: Convert point cloud to CSV for editing
    print(f"\n2. Converting point cloud to CSV for editing...")
    pointcloud_csv_path = convert_pointcloud_to_csv(pointcloud_path, pointcloud_csv_file)
    print(f"   Point cloud CSV saved to {pointcloud_csv_path}")
    print(f"   This CSV file contains only position (x,y,z) and color (r,g,b) data.")
    print(f"   You can now edit this CSV file with any text editor or spreadsheet software.")
    
    # Step 3: Simulate editing the CSV file
    print(f"\n3. Simulating CSV editing - modifying colors...")
    modify_csv_colors(pointcloud_csv_path, pointcloud_csv_path)  # Edit in place
    print(f"   CSV file edited: {pointcloud_csv_path}")
    
    # Step 4: Convert edited CSV back to point cloud
    print(f"\n4. Converting edited CSV back to point cloud...")
    edited_pointcloud_path = convert_csv_to_pointcloud(pointcloud_csv_path, edited_pointcloud_file)
    print(f"   Edited point cloud saved to {edited_pointcloud_path}")

    # Step 5: Convert point cloud back to 3DGS
    print(f"\n5. Converting edited point cloud back to 3D Gaussian Splatting...")
    restored_path = convert_pointcloud_to_3dgs(
        edited_pointcloud_path,
        input_3dgs_file,
        output_3dgs_file
    )
    print(f"   Restored 3D Gaussian Splatting file saved to {restored_path}")
    print("\nWorkflow complete!")


def modify_csv_colors(input_csv, output_csv):
    """
    Read and write CSV file without modifying colors, preserving original appearance.
    
    Args:
        input_csv (str): Input CSV path
        output_csv (str): Output CSV path
    """
    # Read the input CSV file
    with open(input_csv, 'r') as f:
        lines = f.readlines()
    
    # Identify header and extract column indices
    header = lines[0].strip().split(',')
    
    try:
        r_idx = header.index('red')
        g_idx = header.index('green')
        b_idx = header.index('blue')
        has_colors = True
    except ValueError:
        try:
            r_idx = header.index('r')
            g_idx = header.index('g')
            b_idx = header.index('b')
            has_colors = True
        except ValueError:
            has_colors = False
    
    modified_lines = [lines[0]]  # Keep the header
    
    # Process each data row without modifying color values
    for i in range(1, len(lines)):
        values = lines[i].strip().split(',')
        
        # No color transformation - keep original colors
        modified_lines.append(','.join(values) + '\n')
    
    # Write the CSV file with preserved colors
    with open(output_csv, 'w') as f:
        f.writelines(modified_lines)


if __name__ == "__main__":
    main()
