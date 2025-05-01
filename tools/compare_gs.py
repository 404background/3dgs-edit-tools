#!/usr/bin/env python3
"""
3D Gaussian Splatting Comparison Tool

This tool compares two 3DGS PLY files by converting them to CSV format and analyzing differences.
The comparison results are output as:
1. A summary of differences found
2. A CSV file containing difference data (optional)
3. A point cloud visualization of the differences (optional)
"""

import os
import sys
import csv
import numpy as np
import pandas as pd
from pathlib import Path
import argparse
import tempfile
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D

# Import the conversion utilities
import sys
import os
# Add the parent directory to the path to import the src package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.gs_to_csv import convert_3dgs_to_csv
from src.csv_to_gs import convert_csv_to_3dgs
from src import color_utils

def read_csv_as_dataframe(csv_path):
    """
    Read a CSV file and return it as a pandas DataFrame for easier comparison
    """
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Error reading CSV file {csv_path}: {e}")
        return None

def compare_dataframes(df1, df2, tolerance=1e-6):
    """
    Compare two dataframes and return:
    1. Boolean mask of differences
    2. DataFrame with differences
    3. Statistics about differences
    """
    if df1 is None or df2 is None:
        return None, None, {"error": "One of the dataframes is None"}
    
    # Check if columns are the same
    if set(df1.columns) != set(df2.columns):
        only_in_df1 = set(df1.columns) - set(df2.columns)
        only_in_df2 = set(df2.columns) - set(df1.columns)
        return None, None, {
            "error": "Column mismatch",
            "only_in_first": list(only_in_df1),
            "only_in_second": list(only_in_df2)
        }
    
    # Check row counts
    row_count_diff = len(df1) - len(df2)
    
    # Find common columns to compare
    common_columns = list(df1.columns)
    
    # If row counts are different, we can only compare the intersection
    if row_count_diff != 0:
        min_rows = min(len(df1), len(df2))
        df1 = df1.iloc[:min_rows]
        df2 = df2.iloc[:min_rows]
    
    # Calculate differences, considering the tolerance for floating point values
    diff_mask = pd.DataFrame()
    for col in common_columns:
        try:
            # Try to convert to numeric for comparison with tolerance
            col1 = pd.to_numeric(df1[col], errors='coerce')
            col2 = pd.to_numeric(df2[col], errors='coerce')
            
            # For numeric columns, use tolerance
            if col1.dtype.kind in 'fc' and col2.dtype.kind in 'fc':  # float or complex
                diff_mask[col] = abs(col1 - col2) > tolerance
            else:
                diff_mask[col] = df1[col] != df2[col]
        except:
            # For non-numeric columns, use exact comparison
            diff_mask[col] = df1[col] != df2[col]
    
    # Calculate difference statistics
    diff_stats = {
        "row_count_diff": row_count_diff,
        "total_rows_compared": min(len(df1), len(df2)),
        "different_rows": diff_mask.any(axis=1).sum(),
        "column_differences": {col: diff_mask[col].sum() for col in common_columns if diff_mask[col].sum() > 0}
    }
    
    # Create a DataFrame containing only differences
    rows_with_diff = diff_mask.any(axis=1)
    diff_df = pd.DataFrame()
    
    for col in common_columns:
        if diff_mask[col].sum() > 0:  # If this column has any differences
            diff_df[f"{col}_file1"] = df1.loc[rows_with_diff, col]
            diff_df[f"{col}_file2"] = df2.loc[rows_with_diff, col]
            diff_df[f"{col}_diff"] = abs(
                pd.to_numeric(df1.loc[rows_with_diff, col], errors='coerce') - 
                pd.to_numeric(df2.loc[rows_with_diff, col], errors='coerce')
            )
    
    return diff_mask, diff_df, diff_stats

def visualize_position_differences(df1, df2, output_path=None, max_points=10000):
    """
    Create a 3D visualization of position differences between two point sets
    """
    # Ensure we have positional columns
    pos_columns = ['x', 'y', 'z']
    if not all(col in df1.columns for col in pos_columns) or not all(col in df2.columns for col in pos_columns):
        print("Error: Position columns (x, y, z) not found in dataframes")
        return False
    
    # Calculate position differences
    diff_x = abs(pd.to_numeric(df1['x'], errors='coerce') - pd.to_numeric(df2['x'], errors='coerce'))
    diff_y = abs(pd.to_numeric(df1['y'], errors='coerce') - pd.to_numeric(df2['y'], errors='coerce'))
    diff_z = abs(pd.to_numeric(df1['z'], errors='coerce') - pd.to_numeric(df2['z'], errors='coerce'))
    
    # Calculate Euclidean distance
    euclidean_diff = np.sqrt(diff_x**2 + diff_y**2 + diff_z**2)
    
    # Create a dataframe with position and difference values
    viz_df = pd.DataFrame({
        'x': df1['x'],
        'y': df1['y'],
        'z': df1['z'],
        'diff': euclidean_diff
    })
    
    # Filter out rows with no difference to highlight the differences
    viz_df = viz_df[viz_df['diff'] > 0]
    
    # If there are too many points, sample a subset
    if len(viz_df) > max_points:
        viz_df = viz_df.sample(max_points)
    
    # Skip visualization if no differences
    if len(viz_df) == 0:
        print("No position differences found to visualize")
        return False
    
    # Create visualization
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create a colormap based on difference magnitude
    norm = Normalize(vmin=viz_df['diff'].min(), vmax=viz_df['diff'].max())
    scatter = ax.scatter(
        viz_df['x'], viz_df['y'], viz_df['z'],
        c=viz_df['diff'],
        cmap='viridis',
        norm=norm,
        alpha=0.7,
        s=10
    )
    
    # Labels and colorbar
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Position Differences Visualization')
    fig.colorbar(scatter, label='Difference Magnitude')
    
    # Save or show the plot
    if output_path:
        plt.savefig(output_path)
        print(f"Visualization saved to {output_path}")
        plt.close(fig)
        return True
    else:
        plt.show()
        return True

def compare_3dgs_files(file1, file2, output_dir=None, tolerance=1e-6, visualize=True):
    """
    Compare two 3DGS files by converting them to CSV and analyzing differences
    
    Args:
        file1 (str): Path to the first 3DGS file
        file2 (str): Path to the second 3DGS file
        output_dir (str, optional): Directory to save output files
        tolerance (float, optional): Tolerance for floating point comparison
        visualize (bool, optional): Whether to create visualization of differences
    
    Returns:
        dict: Statistics about the differences found
    """
    if not os.path.exists(file1) or not os.path.exists(file2):
        return {"error": f"One or both files do not exist: {file1}, {file2}"}
    
    # Create temporary directory for intermediary files if no output dir specified
    if output_dir is None:
        temp_dir = tempfile.mkdtemp()
        output_dir = temp_dir
    else:
        os.makedirs(output_dir, exist_ok=True)
        temp_dir = None
    
    try:
        # Convert both files to CSV
        csv1_path, _ = convert_3dgs_to_csv(file1, 
                                   os.path.join(output_dir, "file1.csv"))
        
        csv2_path, _ = convert_3dgs_to_csv(file2, 
                                   os.path.join(output_dir, "file2.csv"))
        
        # Read CSV files
        df1 = read_csv_as_dataframe(csv1_path)
        df2 = read_csv_as_dataframe(csv2_path)
        
        # Compare data
        diff_mask, diff_df, diff_stats = compare_dataframes(df1, df2, tolerance)
        
        # Save diff dataframe if there are differences
        if diff_df is not None and len(diff_df) > 0:
            diff_csv_path = os.path.join(output_dir, "differences.csv")
            diff_df.to_csv(diff_csv_path, index=False)
            diff_stats["diff_csv"] = diff_csv_path
            
            # Visualize differences if requested
            if visualize and df1 is not None and df2 is not None:
                viz_path = os.path.join(output_dir, "diff_visualization.png")
                if visualize_position_differences(df1, df2, viz_path):
                    diff_stats["visualization"] = viz_path
        
        return diff_stats
    
    except Exception as e:
        return {"error": f"Error during comparison: {str(e)}"}
    
    finally:
        # Clean up temporary directory if created
        if temp_dir and os.path.exists(temp_dir) and not output_dir:
            import shutil
            shutil.rmtree(temp_dir)

def main():
    parser = argparse.ArgumentParser(description='Compare two 3DGS files')
    parser.add_argument('file1', type=str, help='Path to the first 3DGS file')
    parser.add_argument('file2', type=str, help='Path to the second 3DGS file')
    parser.add_argument('--output-dir', '-o', type=str, default=None, 
                        help='Directory to save output files')
    parser.add_argument('--tolerance', '-t', type=float, default=1e-6,
                        help='Tolerance for floating point comparison')
    parser.add_argument('--no-visualization', action='store_true',
                        help='Skip creating visualization of differences')
    
    args = parser.parse_args()
    
    result = compare_3dgs_files(
        args.file1, args.file2, 
        args.output_dir,
        args.tolerance,
        not args.no_visualization
    )
    
    # Print results
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    print("\n==== 3DGS File Comparison Results ====")
    print(f"File 1: {args.file1}")
    print(f"File 2: {args.file2}")
    
    if result.get("row_count_diff", 0) != 0:
        print(f"\nRow count difference: {result['row_count_diff']}")
        if result['row_count_diff'] > 0:
            print(f"  File 1 has {result['row_count_diff']} more rows than File 2")
        else:
            print(f"  File 2 has {abs(result['row_count_diff'])} more rows than File 1")
    
    print(f"\nTotal rows compared: {result.get('total_rows_compared', 0)}")
    print(f"Rows with differences: {result.get('different_rows', 0)}")
    
    if result.get("column_differences"):
        print("\nColumn differences summary:")
        for col, count in result["column_differences"].items():
            print(f"  {col}: {count} differences")
    
    if "diff_csv" in result:
        print(f"\nDetailed differences saved to: {result['diff_csv']}")
    
    if "visualization" in result:
        print(f"Visualization saved to: {result['visualization']}")
    
    if result.get("different_rows", 0) == 0 and result.get("row_count_diff", 0) == 0:
        print("\nResult: The files are identical (within the specified tolerance)")
    else:
        print("\nResult: The files are different")

if __name__ == "__main__":
    main()
