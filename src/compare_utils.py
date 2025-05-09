"""
Comparison utilities for 3DGS Editor.

This module contains common functions for comparing point cloud and mesh data
used in the 3DGS Editor library.
"""

import numpy as np
import os
import csv
try:
    import pandas as pd
except ImportError:
    pd = None

from .utils import ensure_directory_exists, write_csv_with_header, print_debug_info


def compare_arrays(arr1, arr2, tolerance=1e-6):
    """
    Compare two numpy arrays with tolerance.
    
    Args:
        arr1 (numpy.ndarray): First array
        arr2 (numpy.ndarray): Second array
        tolerance (float): Tolerance for floating-point comparison
        
    Returns:
        tuple: (diff_mask, diff_ratio) - Boolean mask for differences and ratio of differences
    """
    # Check if shapes are the same
    if arr1.shape != arr2.shape:
        # Create a mask of True with the minimum shape
        min_rows = min(arr1.shape[0], arr2.shape[0])
        min_cols = min(arr1.shape[1], arr2.shape[1]) if len(arr1.shape) > 1 else 1
        
        # Compare arrays with the minimum shape
        if len(arr1.shape) > 1:
            diff_mask = np.abs(arr1[:min_rows, :min_cols] - arr2[:min_rows, :min_cols]) > tolerance
        else:
            diff_mask = np.abs(arr1[:min_rows] - arr2[:min_rows]) > tolerance
            
        # Add True for extra elements
        shape_diff = True
    else:
        diff_mask = np.abs(arr1 - arr2) > tolerance
        shape_diff = False
    
    # Calculate ratio of differences
    diff_ratio = np.sum(diff_mask) / diff_mask.size if diff_mask.size > 0 else 1.0
    
    return diff_mask, diff_ratio, shape_diff


def compare_dataframes(df1, df2, tolerance=1e-6):
    """
    Compare two dataframes and return:
    1. Boolean mask of differences
    2. DataFrame with differences
    3. Statistics about differences
    
    Args:
        df1 (pandas.DataFrame): First dataframe
        df2 (pandas.DataFrame): Second dataframe
        tolerance (float): Tolerance for floating-point comparison
        
    Returns:
        tuple: (diff_mask, diff_df, stats) - Difference mask, dataframe with differences, and statistics
    """
    if pd is None:
        raise ImportError("pandas is required for dataframe comparison. Install with: pip install pandas")
    
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
            # For non-numeric columns, use direct comparison
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


def save_differences_to_csv(diff_df, output_file):
    """
    Save differences to a CSV file.
    
    Args:
        diff_df (pandas.DataFrame): Dataframe with differences
        output_file (str): Output CSV file path
        
    Returns:
        str: Path to the saved CSV file
    """
    if pd is None:
        raise ImportError("pandas is required for saving differences. Install with: pip install pandas")
    
    ensure_directory_exists(output_file)
    diff_df.to_csv(output_file, index=False)
    print(f"Difference data saved to: {output_file}")
    return output_file


def point_cloud_distance(cloud1, cloud2, max_distance=float('inf')):
    """
    Calculate distance between two point clouds.
    
    Args:
        cloud1 (numpy.ndarray): First point cloud coordinates (N x 3)
        cloud2 (numpy.ndarray): Second point cloud coordinates (M x 3)
        max_distance (float): Maximum distance to consider
        
    Returns:
        tuple: (distances, correspondence_indices) - Distances and indices of corresponding points
    """
    try:
        import open3d as o3d
    except ImportError:
        raise ImportError("open3d is required for point cloud distance calculation. Install with: pip install open3d")
    
    # Convert to Open3D format
    pcd1 = o3d.geometry.PointCloud()
    pcd1.points = o3d.utility.Vector3dVector(cloud1)
    
    pcd2 = o3d.geometry.PointCloud()
    pcd2.points = o3d.utility.Vector3dVector(cloud2)
    
    # Build KD-tree for fast nearest neighbor search
    pcd_tree = o3d.geometry.KDTreeFlann(pcd2)
    
    distances = []
    correspondence_indices = []
    
    for i, point in enumerate(cloud1):
        # Find nearest neighbor
        k, idx, squared_dist = pcd_tree.search_knn_vector_3d(point, 1)
        
        distance = np.sqrt(squared_dist[0])
        if distance <= max_distance:
            distances.append(distance)
            correspondence_indices.append((i, idx[0]))
    
    return np.array(distances), correspondence_indices


def visualize_point_cloud_differences(cloud1, cloud2, distances, indices, output_file=None, 
                                      colormap_name='jet', max_distance=None):
    """
    Visualize differences between two point clouds.
    
    Args:
        cloud1 (numpy.ndarray): First point cloud coordinates (N x 3)
        cloud2 (numpy.ndarray): Second point cloud coordinates (M x 3)
        distances (numpy.ndarray): Distances between corresponding points
        indices (list): List of (idx1, idx2) tuples for corresponding points
        output_file (str, optional): Output file path for visualization
        colormap_name (str): Colormap name for visualization
        max_distance (float, optional): Maximum distance for color scale
        
    Returns:
        str: Path to the saved visualization file if output_file is provided
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib import cm
        from mpl_toolkits.mplot3d import Axes3D
    except ImportError:
        raise ImportError("matplotlib is required for visualization. Install with: pip install matplotlib")
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Determine color scale based on distances
    if max_distance is None:
        max_distance = np.max(distances) if len(distances) > 0 else 1.0
    
    # Get colormap
    cmap = cm.get_cmap(colormap_name)
    
    # Plot points with colors based on distances
    idx1_list = [idx1 for idx1, _ in indices]
    points_to_plot = cloud1[idx1_list]
    
    # Normalize distances for colormap
    norm_distances = np.array(distances) / max_distance
    colors = cmap(norm_distances)
    
    # Plot points
    ax.scatter(points_to_plot[:, 0], points_to_plot[:, 1], points_to_plot[:, 2], 
              c=colors, s=10, alpha=0.7)
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap)
    sm.set_array(norm_distances)
    cbar = plt.colorbar(sm)
    cbar.set_label('Distance between corresponding points')
    
    # Set labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Point Cloud Difference Visualization')
    
    # Set equal aspect ratio
    max_range = np.array([
        points_to_plot[:, 0].max() - points_to_plot[:, 0].min(),
        points_to_plot[:, 1].max() - points_to_plot[:, 1].min(),
        points_to_plot[:, 2].max() - points_to_plot[:, 2].min()
    ]).max() / 2.0
    
    mid_x = (points_to_plot[:, 0].max() + points_to_plot[:, 0].min()) / 2
    mid_y = (points_to_plot[:, 1].max() + points_to_plot[:, 1].min()) / 2
    mid_z = (points_to_plot[:, 2].max() + points_to_plot[:, 2].min()) / 2
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    # Save or show
    if output_file:
        ensure_directory_exists(output_file)
        plt.savefig(output_file, dpi=300)
        print(f"Visualization saved to: {output_file}")
        plt.close(fig)
        return output_file
    else:
        plt.tight_layout()
        plt.show()
        return None
