"""
File handling utilities for 3DGS Editor.

This module contains common functions for reading and writing different file formats
used in the 3DGS Editor library.
"""

import os
import numpy as np
from .utils import ensure_directory_exists, auto_output_filename


def read_ply_header(file_obj):
    """
    Read and parse the PLY header.
    
    Args:
        file_obj: File object opened in binary mode
        
    Returns:
        tuple: (properties, is_binary, header_lines) - List of properties, binary flag,
               and number of header lines read
    """
    properties = []
    is_binary = False
    header_lines = 0
    line = file_obj.readline().decode('utf-8').strip()
    header_lines += 1
    
    if not line.startswith("ply"):
        raise ValueError("Not a valid PLY file")
    
    # Read header
    while True:
        line = file_obj.readline().decode('utf-8').strip()
        header_lines += 1
        
        if line == "end_header":
            break
        
        if line.startswith("format"):
            if "binary" in line:
                is_binary = True
        
        if line.startswith("property"):
            # Extract property name
            parts = line.split()
            if len(parts) >= 3:
                properties.append(parts[-1])
    
    return properties, is_binary, header_lines


def extract_ply_footer(ply_filename, include_end_header=False):
    """
    Extract footer information from a PLY file.
    
    Args:
        ply_filename (str): Path to the PLY file
        include_end_header (bool): Whether to include the "end_header" line
        
    Returns:
        str: Footer contents or empty string if no footer
    """
    with open(ply_filename, 'rb') as f:
        # Read and parse header to determine binary/text and number of header lines
        properties, is_binary, header_lines = read_ply_header(f)
        
    # Read entire file as text and extract footer
    with open(ply_filename, 'r', encoding='utf-8', errors='ignore') as f:
        all_lines = f.readlines()
    
    # If binary, we don't attempt to extract footer
    if is_binary:
        return ""
    
    # Determine the actual header ending line
    header_end = 0
    for i, line in enumerate(all_lines):
        if line.strip() == "end_header":
            header_end = i
            break
    
    if include_end_header:
        return "".join(all_lines[:header_end+1])
    else:
        return "".join(all_lines[:header_end])


def write_ply_with_header_footer(output_filename, header_content, data_content, footer_content=""):
    """
    Write a PLY file with specified header, data, and footer.
    
    Args:
        output_filename (str): Output PLY file path
        header_content (str): Header content as string
        data_content (str): Data content as string
        footer_content (str): Footer content as string, if any
        
    Returns:
        str: Path to the written PLY file
    """
    ensure_directory_exists(output_filename)
    with open(output_filename, 'w') as f:
        f.write(header_content)
        if not header_content.endswith('\n'):
            f.write('\n')
        f.write("end_header\n")
        f.write(data_content)
        if footer_content:
            f.write(footer_content)
    
    print(f"PLY file saved: {output_filename}")
    return output_filename


def generate_ply_header(properties, vertex_count, format_type="ascii 1.0"):
    """
    Generate a PLY header with specified properties.
    
    Args:
        properties (list): List of property tuples (name, type)
        vertex_count (int): Number of vertices
        format_type (str): PLY format type, default is "ascii 1.0"
        
    Returns:
        str: Generated PLY header
    """
    header = [
        "ply",
        f"format {format_type}",
        f"element vertex {vertex_count}",
    ]
    
    for prop_name, prop_type in properties:
        header.append(f"property {prop_type} {prop_name}")
    
    return "\n".join(header)
