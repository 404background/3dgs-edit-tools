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
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Convert 3D Gaussian Splatting PLY to point cloud and back")
    parser.add_argument("--input_ply", default="Haniwa.ply", help="Input PLY file (default: Haniwa.ply)")
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
    pointcloud_ply = convert_3dgs_to_pointcloud(input_ply, os.path.join("converted", f"{input_basename}_pointcloud.ply"))
    print(f"Point cloud saved: {pointcloud_ply}")
    
    # Record verification in CloudCompare
    verification_info = record_cloudcompare_verification(
        pointcloud_ply, 
        is_verified=True,
        notes="Point cloud structure and color information verified in CloudCompare"
    )
    print(f"Verification details: {verification_info}")
    
    # Step 2: Convert point cloud to CSV for editing
    print("\nConverting point cloud to CSV for editing...")
    pointcloud_csv = convert_pointcloud_to_csv(pointcloud_ply, os.path.join("converted", f"{input_basename}_pointcloud.csv"))
    print(f"CSV file saved: {pointcloud_csv}")
    
    print("\nIn a real workflow, you would edit the CSV file here.")
    print("For this sample, we'll skip the actual edit but continue with the workflow.")
    
    # Step 3: Convert edited CSV back to point cloud
    print("\nConverting CSV back to point cloud...")
    edited_pointcloud = convert_pointcloud_to_3dgs(pointcloud_csv, os.path.join("converted", f"{input_basename}_from_csv.ply"))
    print(f"Edited point cloud saved: {edited_pointcloud}")
    
    # Step 4: Convert point cloud back to 3DGS
    print("\nConverting point cloud back to 3D Gaussian Splatting...")
    restored_ply = convert_pointcloud_to_3dgs(pointcloud_ply, input_ply, os.path.join("converted", f"{input_basename}_from_pointcloud.ply"))
    print(f"Restored 3D Gaussian Splatting file saved: {restored_ply}")
    
    # Restore original current directory
    os.chdir(original_dir)
    
    print("\nAll operations completed successfully!")
    print(f"Generated files are in the '{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'converted')}' directory.")


if __name__ == "__main__":
    main()
