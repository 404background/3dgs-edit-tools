import struct
import csv
import os
import numpy as np
from . import color_utils


def convert_3dgs_to_csv(ply_filename, csv_filename=None, footer_filename=False):
    """
    Convert 3D Gaussian Splatting format (.ply) data to CSV format
    
    Args:
        ply_filename (str): Path to the input PLY file
        csv_filename (str, optional): Path to the output CSV file. If not specified, it's automatically generated from the input filename
        footer_filename (str/bool, optional): Path to save the footer data. Default is False (no footer file created).
                                           Set to None for backward compatibility (will not create a file).
        
    Returns:
        tuple: (csv_filename, footer_filename) - Paths of the generated files (footer_filename is only kept for backwards compatibility)
    """
    # Automatically generate output filename
    if csv_filename is None:
        base_name = os.path.splitext(ply_filename)[0]
        csv_filename = f"{base_name}.csv"
    
    # No longer automatically generate footer_filename - only use if explicitly provided

    with open(ply_filename, "rb") as f:
        content = f.read()

    # Find the end of header position
    header_end = content.find(b'end_header\n') + len(b'end_header\n')
    header = content[:header_end].decode("ascii")

    # Parse header
    lines = header.splitlines()
    vertex_count = 0
    properties = []

    for line in lines:
        if line.startswith("element vertex"):
            vertex_count = int(line.split()[-1])
        elif line.startswith("property float"):
            properties.append(line.split()[-1])

    num_floats = len(properties)
    expected_data_size = vertex_count * num_floats * 4  # float32 = 4 bytes
    
    data_start = header_end
    data_end = data_start + expected_data_size

    # Get binary data section (footer section is not needed)
    data_section = content[data_start:data_end]

    # Convert binary data to float
    data = []
    for i in range(vertex_count):
        start = i * num_floats * 4
        end = start + num_floats * 4
        floats = struct.unpack("<" + "f" * num_floats, data_section[start:end])
        data.append(list(floats))  # Convert to list for easier modification

    # Detect spherical harmonic color coefficients using color_utils
    r_idx, g_idx, b_idx, is_sh_color = color_utils.detect_color_properties(properties)
    
    # If we have color coefficients, normalize them to a more user-friendly range for editing
    if r_idx is not None and g_idx is not None and b_idx is not None:
        color_props = [properties[i] for i in [r_idx, g_idx, b_idx]]
        print(f"Detected color properties: {color_props}, SH color: {is_sh_color}")
        
        # Extract color values for analysis and normalization
        color_values = np.array([[data[row_idx][col_idx] for col_idx in [r_idx, g_idx, b_idx]] 
                                for row_idx in range(len(data))])
        
        # Use color_utils to normalize colors for easier editing
        normalized_colors, min_val, max_val, is_signed = color_utils.normalize_color_for_editing(color_values, is_sh_color)
        print(f"Original color range: {min_val} to {max_val}, signed: {is_signed}")
        
        # Replace the color values with normalized versions
        for row_idx in range(len(data)):
            data[row_idx][r_idx] = normalized_colors[row_idx][0]
            data[row_idx][g_idx] = normalized_colors[row_idx][1]
            data[row_idx][b_idx] = normalized_colors[row_idx][2]
        
        print("Color values normalized to 0-1 range for easier editing")

    # Save to CSV
    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(properties)
        writer.writerows(data)
    
    print(f"Successfully converted 3D Gaussian Splatting data to CSV format ({vertex_count} vertices)")
    
    # If footer_filename is provided and not False, create an empty file for backwards compatibility
    if footer_filename and footer_filename is not False:
        with open(footer_filename, "wb") as f:
            f.write(b'')
        print(f"Note: Footer file {footer_filename} created but is empty (footers no longer used)")
    
    return csv_filename, footer_filename


def main():
    """Entry point for command-line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert 3D Gaussian Splatting data to CSV format')
    parser.add_argument('input_ply', help='Input PLY file')
    parser.add_argument('--output_csv', help='Output CSV filename (default: input_filename.csv)')
    parser.add_argument('--footer', help='Footer filename (deprecated, not used)', default=False)
    
    args = parser.parse_args()
    
    csv_path, _ = convert_3dgs_to_csv(
        args.input_ply, 
        args.output_csv,
        args.footer
    )
    
    print(f"Conversion complete: CSV → {csv_path}")


if __name__ == "__main__":
    main()
