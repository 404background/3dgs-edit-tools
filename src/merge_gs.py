#!/usr/bin/env python3
"""
3D Gaussian Splatting Merge Module

This module provides functions to merge two 3DGS files by converting them to CSV and combining the data.
"""

import os
import sys
import csv
import numpy as np
import pandas as pd
import argparse

from .gs_to_csv import convert_3dgs_to_csv
from .csv_to_gs import convert_csv_to_3dgs

def merge_3dgs_files(file1, file2, output_file=None, transform=None):
    """
    Merge two 3D Gaussian Splatting files by combining their data

    Args:
        file1 (str): Path to the first 3DGS file
        file2 (str): Path to the second 3DGS file
        output_file (str, optional): Path to the output merged 3DGS file
        transform (dict, optional): Optional transformation to apply to the second file
                                   e.g. {'translate': [0.1, 0, 0]} for 10cm translation on X axis
    
    Returns:
        str: Path of the generated merged 3DGS file
    """
    if not os.path.exists(file1) or not os.path.exists(file2):
        raise ValueError(f"One or both files do not exist: {file1}, {file2}")
    
    # Automatically generate output filename if not specified
    if output_file is None:
        base_name1 = os.path.splitext(os.path.basename(file1))[0]
        base_name2 = os.path.splitext(os.path.basename(file2))[0]
        output_file = f"{base_name1}_merged_{base_name2}.ply"
    
    # Convert both files to CSV
    print(f"Converting {file1} to CSV...")
    csv1_path, _ = convert_3dgs_to_csv(file1, None)
    
    print(f"Converting {file2} to CSV...")
    csv2_path, _ = convert_3dgs_to_csv(file2, None)
    
    # Read CSV files
    print("Loading CSV data...")
    df1 = pd.read_csv(csv1_path)
    df2 = pd.read_csv(csv2_path)
    
    # Check if the structure of the two files is compatible
    if set(df1.columns) != set(df2.columns):
        print("Warning: The two files have different column structures. Using columns from the first file.")
        missing_cols = set(df1.columns) - set(df2.columns)
        for col in missing_cols:
            df2[col] = 0.0  # Add missing columns with default values
        df2 = df2[df1.columns]  # Reorder columns to match first file
    
    # Apply transformations to the second file if specified
    if transform is not None:
        df2 = apply_transformation(df2, transform)

    # Combine the data
    df_merged = pd.concat([df1, df2], ignore_index=True)
    
    # Save merged data to CSV
    merged_csv_path = os.path.splitext(output_file)[0] + "_merged.csv"
    df_merged.to_csv(merged_csv_path, index=False)
    print(f"Merged data saved to CSV: {merged_csv_path}")
    
    # Convert merged CSV back to 3DGS format
    print(f"Converting merged CSV to 3DGS format...")
    output_ply = convert_csv_to_3dgs(merged_csv_path, None, output_file)
    print(f"Merged 3DGS file created: {output_file}")
    
    return output_file

def apply_transformation(df, transform):
    """
    Apply transformation to the position data in the dataframe
    
    Args:
        df (pandas.DataFrame): Dataframe with 3DGS data
        transform (dict): Transformation parameters
    
    Returns:
        pandas.DataFrame: Transformed dataframe
    """
    # Make a copy to avoid modifying the original dataframe
    transformed_df = df.copy()
    
    # Find the position columns
    x_col, y_col, z_col = None, None, None
    for col in df.columns:
        if col in ['x', 'pos_0']:
            x_col = col
        elif col in ['y', 'pos_1']:
            y_col = col
        elif col in ['z', 'pos_2']:
            z_col = col
    
    if x_col is None or y_col is None or z_col is None:
        print("Warning: Position columns not found, no transformation applied")
        return df
    
    # Apply translation if specified
    if 'translate' in transform and len(transform['translate']) == 3:
        tx, ty, tz = transform['translate']
        transformed_df[x_col] = df[x_col] + tx
        transformed_df[y_col] = df[y_col] + ty
        transformed_df[z_col] = df[z_col] + tz
        print(f"Applied translation: [{tx}, {ty}, {tz}]")
    
    # Apply scale if specified
    if 'scale' in transform and len(transform['scale']) == 3:
        sx, sy, sz = transform['scale']
        transformed_df[x_col] = df[x_col] * sx
        transformed_df[y_col] = df[y_col] * sy
        transformed_df[z_col] = df[z_col] * sz
        print(f"Applied scaling: [{sx}, {sy}, {sz}]")
    
    return transformed_df

def main():
    """
    Command-line interface for merging 3DGS files
    """
    parser = argparse.ArgumentParser(description='Merge two 3DGS files')
    parser.add_argument('file1', type=str, help='Path to the first 3DGS file')
    parser.add_argument('file2', type=str, help='Path to the second 3DGS file')
    parser.add_argument('--output', '-o', type=str, default=None, 
                        help='Path to the output merged 3DGS file')
    parser.add_argument('--translate-x', type=float, default=0.0,
                        help='Translation along X axis for the second file')
    parser.add_argument('--translate-y', type=float, default=0.0,
                        help='Translation along Y axis for the second file')
    parser.add_argument('--translate-z', type=float, default=0.0,
                        help='Translation along Z axis for the second file')
    parser.add_argument('--scale-x', type=float, default=1.0,
                        help='Scale factor for X axis for the second file')
    parser.add_argument('--scale-y', type=float, default=1.0,
                        help='Scale factor for Y axis for the second file')
    parser.add_argument('--scale-z', type=float, default=1.0,
                        help='Scale factor for Z axis for the second file')
    
    args = parser.parse_args()
    
    # Create transformation dictionary
    transform = {
        'translate': [args.translate_x, args.translate_y, args.translate_z],
        'scale': [args.scale_x, args.scale_y, args.scale_z]
    }
    
    # Skip transformation if all values are default
    if all(x == 0 for x in transform['translate']) and all(x == 1 for x in transform['scale']):
        transform = None
    
    try:
        output_file = merge_3dgs_files(args.file1, args.file2, args.output, transform)
        print(f"\nSuccessfully merged 3DGS files:")
        print(f"- File 1: {args.file1}")
        print(f"- File 2: {args.file2}")
        print(f"- Output: {output_file}")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
