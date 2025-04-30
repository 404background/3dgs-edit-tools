import struct
import os
import numpy as np
from .color_utils import detect_color_properties, get_color_value_range, store_sh_color_range


def convert_3dgs_to_pointcloud(ply_filename, output_ply_filename=None):
    """
    Convert 3D Gaussian Splatting format (.ply) to a standard point cloud PLY file with only
    position and color information.
    
    Args:
        ply_filename (str): Path to the input 3D Gaussian Splatting PLY file
        output_ply_filename (str, optional): Path to the output point cloud PLY file. 
                                             If not specified, it's automatically generated from the input filename
        
    Returns:
        str: Path of the generated PLY file
    """
    # Automatically generate output filename
    if output_ply_filename is None:
        base_name = os.path.splitext(ply_filename)[0]
        output_ply_filename = f"{base_name}_pointcloud.ply"

    with open(ply_filename, "rb") as f:
        content = f.read()

    # Find the end of header position
    header_end = content.find(b'end_header\n') + len(b'end_header\n')
    header = content[:header_end].decode("ascii")

    # Parse header
    lines = header.splitlines()
    vertex_count = 0
    properties = []
    property_types = {}
    original_color_type = "uchar"  # Default color type

    for line in lines:
        if line.startswith("element vertex"):
            vertex_count = int(line.split()[-1])
        elif line.startswith("property"):
            parts = line.split()
            prop_type = parts[1]
            prop_name = parts[2]
            properties.append(prop_name)
            property_types[prop_name] = prop_type
            
            # Detect original color type
            if prop_name in ["red", "green", "blue", "r", "g", "b"]:
                original_color_type = prop_type

    num_floats = len(properties)
    expected_data_size = vertex_count * num_floats * 4  # assuming float32 = 4 bytes
    
    data_start = header_end
    data_end = data_start + expected_data_size

    # Get the binary data section
    data_section = content[data_start:data_end]

    # Convert binary data to float values
    points = []
    colors = []
    sh_colors = []
    
    # Find the indices of position and color properties
    x_idx = properties.index('x')
    y_idx = properties.index('y')
    z_idx = properties.index('z')
    
    # Find color information using the utility function
    r_idx, g_idx, b_idx, is_sh_color = detect_color_properties(properties)

    # Extract position and color data
    for i in range(vertex_count):
        start = i * num_floats * 4
        end = start + num_floats * 4
        values = struct.unpack("<" + "f" * num_floats, data_section[start:end])
        
        point = [values[x_idx], values[y_idx], values[z_idx]]
        points.append(point)
        
        # Add color if available, otherwise use default white
        if r_idx is not None and g_idx is not None and b_idx is not None:
            # Collect SH colors for range detection
            if is_sh_color:
                sh_colors.append([values[r_idx], values[g_idx], values[b_idx]])
            
            # Process color values based on type
            if is_sh_color:
                # Store raw SH colors for now, we'll process them after determining the range
                colors.append([values[r_idx], values[g_idx], values[b_idx]])
            else:
                # Normal color processing
                if property_types.get(properties[r_idx], "") == "float":
                    # If values are in 0-1 range, multiply by 255 to scale to 0-255
                    if 0 <= values[r_idx] <= 1.0 and 0 <= values[g_idx] <= 1.0 and 0 <= values[b_idx] <= 1.0:
                        r = int(values[r_idx] * 255)
                        g = int(values[g_idx] * 255)
                        b = int(values[b_idx] * 255)
                    else:
                        # If values are in 0-255 range, use them directly
                        r = max(0, min(255, int(values[r_idx])))
                        g = max(0, min(255, int(values[g_idx])))
                        b = max(0, min(255, int(values[b_idx])))
                else:
                    # For uchar type, use values directly
                    r = max(0, min(255, int(values[r_idx])))
                    g = max(0, min(255, int(values[g_idx])))
                    b = max(0, min(255, int(values[b_idx])))
                colors.append([r, g, b])
        else:
            colors.append([255, 255, 255])  # Default white color

    # For SH colors, properly normalize based on actual range
    if is_sh_color and sh_colors:
        min_val, max_val, is_signed = get_color_value_range(sh_colors)
        store_sh_color_range(min_val, max_val)
        
        # Normalize SH colors to 0-1 range
        for i in range(len(colors)):
            # Properly normalize from the actual range to 0-1
            r_normalized = (colors[i][0] - min_val) / (max_val - min_val)
            g_normalized = (colors[i][1] - min_val) / (max_val - min_val)
            b_normalized = (colors[i][2] - min_val) / (max_val - min_val)
            
            # Convert to 0-255 range for PLY
            r = int(max(0, min(1, r_normalized)) * 255)
            g = int(max(0, min(1, g_normalized)) * 255)
            b = int(max(0, min(1, b_normalized)) * 255)
            colors[i] = [r, g, b]

    points = np.array(points)
    colors = np.array(colors)

    # Create standard PLY file with position and color data
    with open(output_ply_filename, 'wb') as f:
        # Write header
        f.write(b"ply\n")
        f.write(b"format binary_little_endian 1.0\n")
        f.write(f"element vertex {vertex_count}\n".encode())
        f.write(b"property float x\n")
        f.write(b"property float y\n")
        f.write(b"property float z\n")
        # Output color type matching the original file's property type
        color_type = original_color_type if original_color_type in ["uchar", "float"] else "uchar"
        f.write(f"property {color_type} red\n".encode())
        f.write(f"property {color_type} green\n".encode())
        f.write(f"property {color_type} blue\n".encode())
        f.write(b"end_header\n")
        
        # Write data
        for i in range(vertex_count):
            f.write(struct.pack('<3f', *points[i]))
            if color_type == "float":
                # Save as float color information (0-1 scale)
                r_float = colors[i][0] / 255.0
                g_float = colors[i][1] / 255.0
                b_float = colors[i][2] / 255.0
                f.write(struct.pack('3f', r_float, g_float, b_float))
            else:
                # Save as uchar color information (0-255 scale)
                f.write(struct.pack('3B', *colors[i]))
    
    return output_ply_filename


def main():
    """Entry point for command-line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert 3D Gaussian Splatting data to standard point cloud PLY')
    parser.add_argument('input_ply', help='Input 3D Gaussian Splatting PLY file')
    parser.add_argument('--output_ply', help='Output point cloud PLY filename (default: input_filename_pointcloud.ply)')
    
    args = parser.parse_args()
    
    output_path = convert_3dgs_to_pointcloud(
        args.input_ply,
        args.output_ply
    )
    
    print(f"Conversion complete: {output_path}")


if __name__ == "__main__":
    main()
