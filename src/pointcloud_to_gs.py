import struct
import os
import numpy as np
from . import color_utils


def convert_pointcloud_to_3dgs(pointcloud_ply, original_3dgs_ply, output_ply=None, metadata_file=None):
    """
    Convert a point cloud PLY file back to 3D Gaussian Splatting format,
    using an original 3DGS file as a reference for structure and metadata.
    
    Args:
        pointcloud_ply (str): Path to the input point cloud PLY file
        original_3dgs_ply (str): Path to the original 3D Gaussian Splatting PLY file
        output_ply (str, optional): Path to the output 3DGS PLY file.
                                    If not specified, it's automatically generated from the input filename
        metadata_file (str, optional): Path to the metadata file saved during conversion.
                                       If not provided, uses original_3dgs_ply directly
        
    Returns:
        str: Path of the generated PLY file
    """
    # Automatically generate output filename
    if output_ply is None:
        base_name = os.path.splitext(pointcloud_ply)[0]
        output_ply = f"{base_name}_3dgs.ply"
    
    # Read the point cloud data
    try:
        points, colors, pointcloud_color_type = read_pointcloud_ply_with_type(pointcloud_ply)
        print(f"Read {len(points)} points from point cloud, color type: {pointcloud_color_type}")
    except Exception as e:
        raise ValueError(f"Failed to read point cloud data: {e}")
    
    # Read the original 3DGS file structure
    try:
        with open(original_3dgs_ply, "rb") as f:
            original_content = f.read()
        
        # Find the end of header position
        header_end = original_content.find(b'end_header\n')
        if header_end == -1:
            raise ValueError("Invalid PLY file format: end_header not found")
        header_end += len(b'end_header\n')
        original_header = original_content[:header_end].decode("ascii")
    except Exception as e:
        raise ValueError(f"Failed to read original 3DGS file: {e}")
    
    # Parse original header
    lines = original_header.splitlines()
    vertex_count = 0
    properties = []
    property_types = {}
    
    for line in lines:
        if line.startswith("element vertex"):
            vertex_count = int(line.split()[-1])
        elif line.startswith("property"):
            parts = line.split()
            if len(parts) < 3:
                continue
            prop_type = parts[1]
            prop_name = parts[2]
            properties.append(prop_name)
            property_types[prop_name] = prop_type
    
    print(f"Original file has {vertex_count} vertices with {len(properties)} properties")
    
    # Check if the point counts match
    if len(points) != vertex_count:
        print(f"WARNING: Point count mismatch - Original: {vertex_count}, Point cloud: {len(points)}")
        # Adjust either the point cloud or the expected vertex count to match
        if len(points) < vertex_count:
            # Pad with the last point if needed
            padding = vertex_count - len(points)
            last_point = points[-1] if len(points) > 0 else [0, 0, 0]
            last_color = colors[-1] if len(colors) > 0 else [255, 255, 255]
            points = np.vstack([points, np.tile(last_point, (padding, 1))])
            colors = np.vstack([colors, np.tile(last_color, (padding, 1))])
            print(f"Padded point cloud with {padding} extra points")
        elif len(points) > vertex_count:
            # Truncate extra points
            points = points[:vertex_count]
            colors = colors[:vertex_count]
            print(f"Truncated point cloud to {vertex_count} points")
    
    num_floats = len(properties)
    expected_data_size = vertex_count * num_floats * 4  # assuming float32 = 4 bytes
    
    # Extract the data section from the original file
    data_start = header_end
    data_end = data_start + expected_data_size
    
    # Safety check for data size
    if data_end > len(original_content):
        print(f"WARNING: Expected data size ({expected_data_size} bytes) exceeds file size")
        data_end = len(original_content)
    
    original_data_section = original_content[data_start:data_end]
    
    # Extract the footer section from the original file
    if data_end < len(original_content):
        footer_section = original_content[data_end:]
    else:
        footer_section = b''
    
    # Find position property indices in original 3DGS data
    try:
        x_idx = properties.index('x')
        y_idx = properties.index('y')
        z_idx = properties.index('z')
    except ValueError as e:
        raise ValueError(f"Missing position property in original file: {e}")
    
    # Find color information in the original file using color_utils
    r_idx, g_idx, b_idx, is_sh_color = color_utils.detect_color_properties(properties)
    original_color_type = "unknown"
    
    if r_idx is not None:
        original_color_type = property_types.get(properties[r_idx], "unknown")
        print(f"Original color type: {original_color_type}, Spherical Harmonics: {is_sh_color}")
    else:
        print("WARNING: Color properties not found in original file, color information will be skipped")
    
    # Read the original data as floats
    original_data = []
    total_values = len(original_data_section) // 4  # Each float is 4 bytes
    expected_values = vertex_count * num_floats
    
    if total_values != expected_values:
        print(f"WARNING: Data size mismatch - Expected {expected_values} values, got {total_values}")
    
    # Safely unpack the values
    try:
        for i in range(min(vertex_count, total_values // num_floats)):
            start = i * num_floats * 4
            end = start + num_floats * 4
            if end <= len(original_data_section):
                values = list(struct.unpack("<" + "f" * num_floats, original_data_section[start:end]))
                original_data.append(values)
            else:
                # If data is truncated, pad with zeros
                values = [0.0] * num_floats
                original_data.append(values)
                print(f"WARNING: Data truncated at vertex {i}")
    except Exception as e:
        raise ValueError(f"Error unpacking original data: {e}")
    
    # If we have fewer data points than expected, pad with zeros
    while len(original_data) < vertex_count:
        original_data.append([0.0] * num_floats)
    
    # Extract original colors for reference if color properties exist
    original_colors = []
    if r_idx is not None and g_idx is not None and b_idx is not None:
        for i in range(len(original_data)):
            original_colors.append([
                original_data[i][r_idx],
                original_data[i][g_idx],
                original_data[i][b_idx]
            ])
    
        # Get color value ranges and debug info
        orig_min, orig_max, is_signed = color_utils.get_color_value_range(original_colors)
        print(f"Color value range: {orig_min} to {orig_max}, signed: {is_signed}")
    
    # Debug color information from point cloud
    if len(colors) > 0:
        color_utils.print_color_debug_info(colors, pointcloud_color_type, False)
    
    # Update position and color information in the original data
    for i in range(min(len(original_data), len(points))):
        # Update position
        original_data[i][x_idx] = points[i][0]
        original_data[i][y_idx] = points[i][1]
        original_data[i][z_idx] = points[i][2]
        
        # Update color if applicable
        if r_idx is not None and g_idx is not None and b_idx is not None and len(colors) > i:
            try:
                # Convert colors using the utility function
                converted_colors = color_utils.convert_colors_between_formats(
                    np.array([colors[i]]),
                    pointcloud_color_type,
                    original_color_type,
                    is_sh_source=False,
                    is_sh_target=is_sh_color,
                    orig_min=orig_min,
                    orig_max=orig_max
                )[0]
                
                original_data[i][r_idx] = converted_colors[0]
                original_data[i][g_idx] = converted_colors[1]
                original_data[i][b_idx] = converted_colors[2]
            except Exception as e:
                print(f"WARNING: Error updating color for vertex {i}: {e}")
    
    # Write the updated 3DGS file
    try:
        with open(output_ply, "wb") as f:
            # Write header
            f.write(original_header.encode("ascii"))
            
            # Write binary data
            for values in original_data:
                f.write(struct.pack("<" + "f" * num_floats, *values))
            
            # Write footer
            f.write(footer_section)
        
        print(f"Successfully wrote {len(original_data)} vertices to output file")
    except Exception as e:
        raise ValueError(f"Failed to write output file: {e}")
    
    return output_ply


def read_pointcloud_ply_with_type(filename):
    """
    Read position and color information from a point cloud PLY file, including color type info.
    
    Args:
        filename (str): Path to the PLY file
        
    Returns:
        tuple: (points, colors, color_type) where:
            - points is a numpy array of (x,y,z) coordinates
            - colors is a numpy array of (r,g,b) values
            - color_type is a string indicating the color data type ("float" or "uchar")
    """
    with open(filename, "rb") as f:
        content = f.read()
    
    # Find the end of header position
    header_end = content.find(b'end_header\n') + len(b'end_header\n')
    header = content[:header_end].decode("ascii")
    
    # Parse header
    lines = header.splitlines()
    vertex_count = 0
    properties = []
    formats = {}
    color_type = "uchar"  # Default
    
    for line in lines:
        if line.startswith("element vertex"):
            vertex_count = int(line.split()[-1])
        elif line.startswith("property"):
            parts = line.split()
            if len(parts) < 3:
                continue
            prop_type = parts[1]  # float, uchar, etc.
            prop_name = parts[2]
            properties.append(prop_name)
            formats[prop_name] = prop_type
            
            # Detect color type
            if prop_name in ["red", "green", "blue", "r", "g", "b"]:
                color_type = prop_type
    
    print(f"Pointcloud has {vertex_count} vertices, color type: {color_type}")
    
    # Determine the format of each vertex
    format_str = "<"  # little endian
    size_sum = 0
    
    for prop in properties:
        if formats[prop] == "float":
            format_str += "f"
            size_sum += 4
        elif formats[prop] == "uchar":
            format_str += "B"
            size_sum += 1
        elif formats[prop] == "double":
            format_str += "d"
            size_sum += 8
        elif formats[prop] == "int":
            format_str += "i"
            size_sum += 4
        elif formats[prop] == "short":
            format_str += "h"
            size_sum += 2
        elif formats[prop] == "uint":
            format_str += "I"
            size_sum += 4
    
    # Extract the data section
    data_section = content[header_end:]
    
    # Let color_utils handle the color property detection
    r_idx, g_idx, b_idx, _ = color_utils.detect_color_properties(properties)
    
    # Find the indices of position properties
    try:
        x_idx = properties.index('x')
        y_idx = properties.index('y')
        z_idx = properties.index('z')
    except ValueError as e:
        raise ValueError(f"Missing position property: {e}")
    
    # Read the binary data
    points = []
    colors = []
    
    for i in range(vertex_count):
        start = i * size_sum
        end = start + size_sum
        values = struct.unpack(format_str, data_section[start:end])
        
        # Extract position
        points.append([values[x_idx], values[y_idx], values[z_idx]])
        
        # Extract color if available
        if r_idx is not None and g_idx is not None and b_idx is not None:
            colors.append([values[r_idx], values[g_idx], values[b_idx]])
        else:
            colors.append([255, 255, 255])  # Default to white if no color
    
    return np.array(points), np.array(colors), color_type


def main():
    """Entry point for command-line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert point cloud PLY to 3D Gaussian Splatting format')
    parser.add_argument('pointcloud_ply', help='Input point cloud PLY file')
    parser.add_argument('original_3dgs', help='Original 3D Gaussian Splatting file to use as reference')
    parser.add_argument('--output_ply', help='Output 3DGS PLY filename (default: input_filename_3dgs.ply)')
    parser.add_argument('--metadata', help='Metadata file saved during original conversion (optional)')
    
    args = parser.parse_args()
    
    output_path = convert_pointcloud_to_3dgs(
        args.pointcloud_ply,
        args.original_3dgs,
        args.output_ply,
        args.metadata
    )
    
    print(f"Conversion complete: {output_path}")


if __name__ == "__main__":
    main()
