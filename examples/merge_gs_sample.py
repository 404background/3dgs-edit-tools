#!/usr/bin/env python3
"""
Sample script demonstrating 3DGS file merging features

This sample:
1. Takes an original PLY file (e.g., Haniwa.ply)
2. Creates a transformed copy (moved 10cm in the X direction)
3. Merges the original and transformed PLY files into a single 3DGS file
4. All output files are saved in the converted folder
"""

import os
import sys
import argparse

# Add the parent directory to the path to import the src package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import merge_3dgs_files, convert_3dgs_to_csv, convert_csv_to_3dgs

def create_transformed_copy(input_ply, output_ply, transformation):
    """
    Create a transformed copy of a 3DGS file
    
    Args:
        input_ply (str): Path to input PLY file
        output_ply (str): Path to output transformed PLY file
        transformation (dict): Dictionary with transformation parameters
    
    Returns:
        str: Path to transformed PLY file
    """
    import pandas as pd
    
    # Convert PLY to CSV
    csv_path, _ = convert_3dgs_to_csv(input_ply)
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Find position columns
    x_col, y_col, z_col = None, None, None
    for col in df.columns:
        if col in ['x', 'pos_0']:
            x_col = col
        elif col in ['y', 'pos_1']:
            y_col = col
        elif col in ['z', 'pos_2']:
            z_col = col
    
    if x_col is None or y_col is None or z_col is None:
        print("Warning: Position columns not found")
        return None
    
    # Apply the transformation
    if 'translate' in transformation:
        tx, ty, tz = transformation['translate']
        df[x_col] = df[x_col] + tx
        df[y_col] = df[y_col] + ty
        df[z_col] = df[z_col] + tz
    
    # Save transformed data to CSV
    transformed_csv_path = os.path.splitext(output_ply)[0] + ".csv"
    df.to_csv(transformed_csv_path, index=False)
    
    # Convert CSV back to PLY
    output_ply_path = convert_csv_to_3dgs(transformed_csv_path, None, output_ply)
    
    return output_ply_path

def main():
    """
    Sample for merging 3DGS files
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Merge 3D Gaussian Splatting files sample")
    parser.add_argument("--input_ply", default="Haniwa.ply", help="Input 3D Gaussian Splatting PLY file")
    parser.add_argument("--translation", type=float, default=0.1, help="Translation distance in X direction for the second model (default: 0.1)")
    args = parser.parse_args()
    
    # Get current directory for correct path resolution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    input_3dgs_file = os.path.join(current_dir, args.input_ply)
    
    # Extract filename without extension for output file naming
    input_filename = os.path.basename(args.input_ply)
    input_base = os.path.splitext(input_filename)[0]
    
    # Make sure the converted directory exists
    converted_dir = os.path.join(current_dir, "converted")
    os.makedirs(converted_dir, exist_ok=True)
    
    # Define paths for transformed and merged files
    transformed_file = os.path.join(converted_dir, f"{input_base}_transformed.ply")
    merged_file = os.path.join(converted_dir, f"{input_base}_merged.ply")
    
    print(f"\n=== 3D GAUSSIAN SPLATTING MERGE WORKFLOW ===")
    
    # Check if input file exists
    if not os.path.exists(input_3dgs_file):
        print(f"Error: Input file not found: {input_3dgs_file}")
        return 1
    
    print(f"Using input file: {input_3dgs_file}")
    
    # Step 1: Create a transformed copy of the input file
    print(f"\n1. Creating transformed copy with {args.translation}m X-axis translation...")
    transformation = {'translate': [args.translation, 0.0, 0.0]}
    transformed_path = create_transformed_copy(input_3dgs_file, transformed_file, transformation)
    print(f"   Transformed file saved to {transformed_path}")
    
    # Step 2: Merge original and transformed files
    print(f"\n2. Merging original and transformed 3DGS files...")
    merged_path = merge_3dgs_files(input_3dgs_file, transformed_path, merged_file)
    print(f"   Merged file saved to {merged_path}")
    
    print("\n=== Merge summary ===")
    print(f"Original file: {input_3dgs_file}")
    print(f"Transformed file: {transformed_path}")
    print(f"Merged file: {merged_path}")
    print(f"\nAll output files were saved in {converted_dir}")
    print("\nTo visualize the result, open the merged file in a 3D Gaussian Splatting viewer.")
    print("You should see two models - the original and its translated copy.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
