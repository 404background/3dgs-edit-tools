"""
Utility functions for 3DGS Editor.

This module contains common utility functions used across multiple components
of the 3DGS Editor library.
"""

import os
import numpy as np
import csv
import warnings


def ensure_directory_exists(filepath):
    """
    Ensure the directory for a file path exists.
    
    Args:
        filepath (str): Path to a file
        
    Returns:
        str: The directory path that was created or already existed
    """
    directory = os.path.dirname(filepath)
    
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    return directory


def auto_output_filename(input_filename, suffix, extension):
    """
    Automatically generate an output filename based on input filename.
    
    Args:
        input_filename (str): Original filename
        suffix (str): Suffix to add before the extension
        extension (str): File extension to use (without the dot)
        
    Returns:
        str: Generated output filename
    """
    base_name = os.path.basename(input_filename)
    name_without_ext = os.path.splitext(base_name)[0]
    parent_dir = os.path.dirname(input_filename)
    
    if parent_dir:
        return os.path.join(parent_dir, f"{name_without_ext}{suffix}.{extension}")
    else:
        return f"{name_without_ext}{suffix}.{extension}"


def detect_coordinate_properties(properties):
    """
    Detect coordinate-related property indices from a property list
    
    Args:
        properties (list): List of property names
        
    Returns:
        tuple: (x_idx, y_idx, z_idx) - Coordinate-related indices
    """
    # Common coordinate property names
    coord_names = [
        ('x', 'y', 'z'),
        ('pos_0', 'pos_1', 'pos_2'),
        ('position_0', 'position_1', 'position_2'),
    ]
    
    # Try to find coordinate properties
    for x_name, y_name, z_name in coord_names:
        try:
            x_idx = properties.index(x_name)
            y_idx = properties.index(y_name)
            z_idx = properties.index(z_name)
            return x_idx, y_idx, z_idx
        except ValueError:
            continue
    
    # If not found, return the first 3 indices as default
    warnings.warn("Coordinate attributes not found. Using the first 3 columns as default.")
    return 0, 1, 2


def detect_quaternion_properties(properties):
    """
    Detect quaternion-related property indices from a property list
    
    Args:
        properties (list): List of property names
        
    Returns:
        tuple: (q0_idx, q1_idx, q2_idx, q3_idx) - Quaternion-related indices or None if not found
    """
    # Common quaternion property names
    quat_names = [
        ('rot_0', 'rot_1', 'rot_2', 'rot_3'),
        ('rotation_0', 'rotation_1', 'rotation_2', 'rotation_3'),
        ('quat_0', 'quat_1', 'quat_2', 'quat_3'),
    ]
    
    # Try to find quaternion properties
    for q0_name, q1_name, q2_name, q3_name in quat_names:
        try:
            q0_idx = properties.index(q0_name)
            q1_idx = properties.index(q1_name)
            q2_idx = properties.index(q2_name)
            q3_idx = properties.index(q3_name)
            return q0_idx, q1_idx, q2_idx, q3_idx
        except ValueError:
            continue
    
    # If not found, return None
    return None


def detect_scale_properties(properties):
    """
    Detect scale-related property indices from a property list
    
    Args:
        properties (list): List of property names
        
    Returns:
        tuple: (sx_idx, sy_idx, sz_idx) - Scale-related indices or None if not found
    """
    # Common scale property names
    scale_names = [
        ('scale_0', 'scale_1', 'scale_2'),
        ('scaling_0', 'scaling_1', 'scaling_2'),
    ]
    
    # Try to find scale properties
    for sx_name, sy_name, sz_name in scale_names:
        try:
            sx_idx = properties.index(sx_name)
            sy_idx = properties.index(sy_name)
            sz_idx = properties.index(sz_name)
            return sx_idx, sy_idx, sz_idx
        except ValueError:
            continue
    
    # If not found, return None
    return None


def read_csv_with_header(csv_filename):
    """
    Read a CSV file with header and return header and data.
    
    Args:
        csv_filename (str): Path to CSV file
        
    Returns:
        tuple: (header, data) - Header list and data as list of lists
    """
    with open(csv_filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        data = list(reader)
        
    return header, data


def write_csv_with_header(csv_filename, header, data):
    """
    Write data to a CSV file with header.
    
    Args:
        csv_filename (str): Path to CSV file
        header (list): Header row
        data (list): List of data rows
        
    Returns:
        str: Path to the written CSV file
    """
    ensure_directory_exists(csv_filename)
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(data)
    
    print(f"CSV file saved: {csv_filename}")
    return csv_filename


def print_debug_info(message, *args, verbose=True):
    """
    Print debug information if verbose mode is enabled.
    
    Args:
        message (str): Message to print
        *args: Additional arguments to print
        verbose (bool, optional): Whether to print debug info. Defaults to True.
    """
    if verbose:
        print(message, *args)


def record_blender_verification(mesh_file, is_verified=True, notes=None):
    """
    Record that a mesh file has been verified in Blender.
    
    This function logs information about mesh files that have been checked
    in Blender for visualization compatibility and quality assessment.
    
    Args:
        mesh_file (str): Path to the mesh file that was verified
        is_verified (bool, optional): Whether the mesh displays correctly. Defaults to True.
        notes (str, optional): Additional notes about the verification. Defaults to None.
        
    Returns:
        dict: Verification information
    """
    verification_info = {
        'file': mesh_file,
        'verified_in_blender': is_verified,
        'verification_date': os.path.getmtime(mesh_file) if os.path.exists(mesh_file) else None,
        'notes': notes or "Display confirmed in Blender"
    }
    
    print(f"Mesh verification in Blender recorded for: {mesh_file}")
    print(f"Status: {'Verified' if is_verified else 'Issues detected'}")
    if notes:
        print(f"Notes: {notes}")
        
    return verification_info


def record_cloudcompare_verification(pointcloud_file, is_verified=True, notes=None):
    """
    Record that a point cloud file has been verified in CloudCompare.
    
    This function logs information about point cloud files that have been checked
    in CloudCompare for visualization compatibility and quality assessment.
    
    Args:
        pointcloud_file (str): Path to the point cloud file that was verified
        is_verified (bool, optional): Whether the point cloud displays correctly. Defaults to True.
        notes (str, optional): Additional notes about the verification. Defaults to None.
        
    Returns:
        dict: Verification information
    """
    verification_info = {
        'file': pointcloud_file,
        'verified_in_cloudcompare': is_verified,
        'verification_date': os.path.getmtime(pointcloud_file) if os.path.exists(pointcloud_file) else None,
        'notes': notes or "Display confirmed in CloudCompare"
    }
    
    print(f"Point cloud verification in CloudCompare recorded for: {pointcloud_file}")
    print(f"Status: {'Verified' if is_verified else 'Issues detected'}")
    if notes:
        print(f"Notes: {notes}")
        
    return verification_info
