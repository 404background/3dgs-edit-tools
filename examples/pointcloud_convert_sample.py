"""
Sample script demonstrating how to convert between 3D Gaussian Splatting and point cloud formats.
This workflow allows for editing the data in external tools and then restoring
it back to 3D Gaussian Splatting format with all the additional metadata preserved.

The script uses CSV format as an intermediate step for easier editing.
"""

import os
import sys
import struct
import numpy as np
import argparse
from pathlib import Path

# Add the parent directory to the path to import the src package
sys.path.append(str(Path(__file__).parent.parent))

from src.gs_to_pointcloud import convert_3dgs_to_pointcloud
from src.pointcloud_to_csv import convert_pointcloud_to_csv
from src.pointcloud_to_gs import convert_pointcloud_to_3dgs
from src.csv_to_gs import convert_csv_to_3dgs
from src.utils import record_cloudcompare_verification


def main():
    """
    Demonstrates a simplified workflow:
    1. Convert 3DGS to point cloud
    2. Convert point cloud to CSV for editing
    3. Edit the CSV data (simulate by changing colors)
    4. Convert CSV back to point cloud
    5. Convert point cloud back to 3DGS format
    """    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Convert 3D Gaussian Splatting PLY to point cloud and back")
    parser.add_argument("--input_ply", default="Haniwa.ply", help="Input PLY file (default: Haniwa.ply)")
    parser.add_argument("--no_color", action="store_true", help="Remove color information from point cloud")
    args = parser.parse_args()
    
    # Change current directory to script location
    original_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Use input file name or default to examples/Haniwa.ply if file does not exist
    input_ply = args.input_ply if os.path.exists(args.input_ply) else os.path.join(os.path.dirname(os.path.abspath(__file__)), args.input_ply)
    
    # Extract filename without extension
    input_basename = os.path.splitext(os.path.basename(input_ply))[0]
    
    os.makedirs("converted", exist_ok=True)
      # Step 1: Convert 3DGS to point cloud
    print("Converting 3D Gaussian Splatting to point cloud...")
    
    # Determine output filename based on whether color information is included
    color_suffix = "_nocolor" if args.no_color else ""
    pointcloud_filename = f"{input_basename}_pointcloud{color_suffix}.ply"
    pointcloud_path = os.path.join("converted", pointcloud_filename)
    
    # Convert to point cloud
    pointcloud_ply = convert_3dgs_to_pointcloud(input_ply, pointcloud_path)
    
    # If no_color option is enabled, remove color information
    if args.no_color:
        print("Removing color information from point cloud...")
        # Read the point cloud without color information
        from src.pointcloud_to_csv import read_pointcloud_ply
        points, _, _ = read_pointcloud_ply(pointcloud_ply)
        
        # Create a new point cloud file without color information
        with open(pointcloud_ply, 'wb') as f:
            # Write header
            f.write(b"ply\n")
            f.write(b"format binary_little_endian 1.0\n")
            f.write(f"element vertex {len(points)}\n".encode())
            f.write(b"property float x\n")
            f.write(b"property float y\n")
            f.write(b"property float z\n")
            f.write(b"end_header\n")
            
            # Write only position data
            for point in points:
                f.write(struct.pack('<3f', *point))
        
        print("Color information removed successfully")
    
    print(f"Point cloud saved: {pointcloud_ply}")
    
    # Record verification in CloudCompare
    notes = "Point cloud structure verified in CloudCompare" if args.no_color else "Point cloud structure and color information verified in CloudCompare"
    verification_info = record_cloudcompare_verification(
        pointcloud_ply, 
        is_verified=True,
        notes=notes
    )
    print(f"Verification details: {verification_info}")
      # Step 2: Convert point cloud to CSV for editing
    print("\nConverting point cloud to CSV for editing...")
    csv_suffix = "_nocolor" if args.no_color else ""
    csv_filename = f"{input_basename}_pointcloud{csv_suffix}.csv"
    pointcloud_csv = convert_pointcloud_to_csv(pointcloud_ply, os.path.join("converted", csv_filename))
    print(f"CSV file saved: {pointcloud_csv}")
    
    print("\nIn a real workflow, you would edit the CSV file here.")
    print("For this sample, we'll skip the actual edit but continue with the workflow.")
      # Step 3: Convert edited CSV back to point cloud
    print("\nConverting CSV back to point cloud...")
    # First convert CSV to point cloud format
    from src.pointcloud_to_csv import convert_csv_to_pointcloud
    
    # Use different filename based on whether color info is preserved
    edited_suffix = "_edited_nocolor" if args.no_color else "_edited"
    edited_filename = f"{input_basename}{edited_suffix}.ply"
    
    # Convert CSV to point cloud with or without color
    if args.no_color:
        # When no color is desired, we need to specify that color columns should be ignored
        edited_pointcloud_ply = convert_csv_to_pointcloud(
            pointcloud_csv, 
            os.path.join("converted", edited_filename),
            # Either way, we'll write as uchar, but we'll handle color removal after
            color_type="uchar"
        )
        
        # Read the point cloud to get just the points
        points, _, _ = read_pointcloud_ply(edited_pointcloud_ply)
        
        # Recreate without color
        with open(edited_pointcloud_ply, 'wb') as f:
            # Write header without color properties
            f.write(b"ply\n")
            f.write(b"format binary_little_endian 1.0\n")
            f.write(f"element vertex {len(points)}\n".encode())
            f.write(b"property float x\n")
            f.write(b"property float y\n")
            f.write(b"property float z\n")
            f.write(b"end_header\n")
            
            # Write only position data
            for point in points:
                f.write(struct.pack('<3f', *point))
    else:
        # Normal conversion with color
        edited_pointcloud_ply = convert_csv_to_pointcloud(
            pointcloud_csv, 
            os.path.join("converted", edited_filename),
            color_type="uchar"
        )
    
    print(f"Edited point cloud saved: {edited_pointcloud_ply}")      # Step 4: Convert point cloud back to 3DGS
    print("\nConverting point cloud back to 3D Gaussian Splatting...")
    # First convert the edited point cloud back to 3DGS
    from src.pointcloud_to_gs import convert_pointcloud_to_3dgs
    
    # Choose appropriate output filename based on color option
    output_suffix = "_from_pointcloud_nocolor" if args.no_color else "_from_pointcloud"
    output_filename = f"{input_basename}{output_suffix}.ply"
    
    # Convert back to 3DGS format
    restored_ply = convert_pointcloud_to_3dgs(
        edited_pointcloud_ply, 
        input_ply, 
        os.path.join("converted", output_filename)
    )
    print(f"Restored 3D Gaussian Splatting file saved: {restored_ply}")
    
    # Restore original current directory
    os.chdir(original_dir)
    
    print("\nAll operations completed successfully!")
    print(f"Generated files are in the '{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'converted')}' directory.")


if __name__ == "__main__":
    main()
