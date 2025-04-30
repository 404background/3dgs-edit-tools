import struct
import os
import csv
import numpy as np


def convert_pointcloud_to_csv(ply_filename, csv_filename=None):
    """
    Convert point cloud PLY file to CSV format for easier editing.
    
    Args:
        ply_filename (str): Path to the input point cloud PLY file
        csv_filename (str, optional): Path to the output CSV file
            If not specified, it's automatically generated from the input filename
        
    Returns:
        str: Path of the generated CSV file
    """
    # Automatically generate output filename
    if csv_filename is None:
        base_name = os.path.splitext(ply_filename)[0]
        csv_filename = f"{base_name}.csv"

    # Read point cloud data
    points, colors, color_type = read_pointcloud_ply(ply_filename)
    
    # Create CSV header - always include x,y,z and r,g,b
    header = ['x', 'y', 'z', 'red', 'green', 'blue']
    
    # Create rows with position and color data
    rows = []
    for i in range(len(points)):
        # If color data uses float (0-1), convert to 0-255 range for better readability in CSV
        if color_type == "float":
            color_vals = [
                min(255, int(colors[i][0] * 255)) if colors[i][0] <= 1.0 else int(colors[i][0]),
                min(255, int(colors[i][1] * 255)) if colors[i][1] <= 1.0 else int(colors[i][1]),
                min(255, int(colors[i][2] * 255)) if colors[i][2] <= 1.0 else int(colors[i][2])
            ]
        else:
            color_vals = [int(colors[i][0]), int(colors[i][1]), int(colors[i][2])]
            
        row = [
            points[i][0],  # x
            points[i][1],  # y
            points[i][2],  # z
            color_vals[0], # red
            color_vals[1], # green
            color_vals[2]  # blue
        ]
        rows.append(row)
    
    # Write data to CSV
    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    
    return csv_filename


def convert_csv_to_pointcloud(csv_filename, output_ply_filename=None, color_type="uchar"):
    """
    Convert CSV file to point cloud PLY format.
    
    Args:
        csv_filename (str): Path to the input CSV file
        output_ply_filename (str, optional): Path to the output point cloud PLY file
            If not specified, it's automatically generated from the input filename
        color_type (str): Type of color data to use in PLY file ('float' or 'uchar')
        
    Returns:
        str: Path of the generated PLY file
    """
    # Automatically generate output filename
    if output_ply_filename is None:
        base_name = os.path.splitext(csv_filename)[0]
        output_ply_filename = f"{base_name}.ply"
    
    # Read CSV data
    with open(csv_filename, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)  # Get header
        rows = list(reader)    # Get all data rows
    
    # Extract column indices
    try:
        x_idx = header.index('x')
        y_idx = header.index('y')
        z_idx = header.index('z')
        r_idx = header.index('red')
        g_idx = header.index('green')
        b_idx = header.index('blue')
    except ValueError:
        # Alternative column names
        try:
            x_idx = header.index('x')
            y_idx = header.index('y')
            z_idx = header.index('z')
            r_idx = header.index('r')
            g_idx = header.index('g')
            b_idx = header.index('b')
        except ValueError:
            raise ValueError("CSV file must contain x,y,z and red,green,blue (or r,g,b) columns")
    
    # Extract point and color data
    points = []
    colors = []
    
    for row in rows:
        if len(row) > max(x_idx, y_idx, z_idx, r_idx, g_idx, b_idx):
            points.append([float(row[x_idx]), float(row[y_idx]), float(row[z_idx])])
            
            # Handle color data - convert to the required type
            if color_type == "float":
                # Convert to float range 0-1 if values are in 0-255 range
                r_val = float(row[r_idx])
                g_val = float(row[g_idx])
                b_val = float(row[b_idx])
                
                # Check if values are in 0-255 range and convert to 0-1
                if r_val > 1.0 or g_val > 1.0 or b_val > 1.0:
                    r_val /= 255.0
                    g_val /= 255.0
                    b_val /= 255.0
                
                colors.append([r_val, g_val, b_val])
            else:
                # Convert to integers in 0-255 range
                r_val = float(row[r_idx])
                g_val = float(row[g_idx])
                b_val = float(row[b_idx])
                
                # If values are in 0-1 range, convert to 0-255
                if r_val <= 1.0 and g_val <= 1.0 and b_val <= 1.0 and (r_val > 0 or g_val > 0 or b_val > 0):
                    r_val *= 255
                    g_val *= 255
                    b_val *= 255
                
                colors.append([int(r_val), int(g_val), int(b_val)])
    
    points = np.array(points)
    colors = np.array(colors)
    
    # Create PLY file
    with open(output_ply_filename, 'wb') as f:
        # Write header
        f.write(b"ply\n")
        f.write(b"format binary_little_endian 1.0\n")
        f.write(f"element vertex {len(points)}\n".encode())
        f.write(b"property float x\n")
        f.write(b"property float y\n")
        f.write(b"property float z\n")
        
        if color_type == "float":
            f.write(b"property float red\n")
            f.write(b"property float green\n")
            f.write(b"property float blue\n")
        else:
            f.write(b"property uchar red\n")
            f.write(b"property uchar green\n")
            f.write(b"property uchar blue\n")
        
        f.write(b"end_header\n")
        
        # Write data
        for i in range(len(points)):
            f.write(struct.pack('<3f', *points[i]))  # Position data
            
            if color_type == "float":
                f.write(struct.pack('<3f', *colors[i]))  # Color as float
            else:
                # Ensure values are within 0-255 range
                r = max(0, min(255, int(colors[i][0])))
                g = max(0, min(255, int(colors[i][1])))
                b = max(0, min(255, int(colors[i][2])))
                f.write(struct.pack('3B', r, g, b))  # Color as uchar
    
    return output_ply_filename


def read_pointcloud_ply(filename):
    """
    Read position and color information from a point cloud PLY file.
    
    Args:
        filename (str): Path to the PLY file
        
    Returns:
        tuple: (points, colors, color_type) where:
            - points is a numpy array of (x,y,z) coordinates
            - colors is a numpy array of (r,g,b) values
            - color_type is a string indicating the data type of colors ("float" or "uchar")
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
    color_type = "uchar"  # Default color type
    
    for line in lines:
        if line.startswith("element vertex"):
            vertex_count = int(line.split()[-1])
        elif line.startswith("property"):
            parts = line.split()
            prop_type = parts[1]  # float, uchar, etc.
            prop_name = parts[2]
            properties.append(prop_name)
            formats[prop_name] = prop_type
            
            # Detect color type
            if prop_name in ["red", "green", "blue", "r", "g", "b"]:
                color_type = prop_type
    
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
    
    # Find the indices of position and color properties
    x_idx = properties.index('x')
    y_idx = properties.index('y')
    z_idx = properties.index('z')
    
    # Try to find color information (could be named differently in different formats)
    try:
        r_idx = properties.index('red')
        g_idx = properties.index('green')
        b_idx = properties.index('blue')
    except ValueError:
        try:
            r_idx = properties.index('r')
            g_idx = properties.index('g')
            b_idx = properties.index('b')
        except ValueError:
            r_idx = g_idx = b_idx = None
    
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
    
    parser = argparse.ArgumentParser(description='Convert between point cloud PLY and CSV formats')
    subparsers = parser.add_subparsers(dest='command', help='command')
    
    # Pointcloud to CSV command
    ply2csv_parser = subparsers.add_parser('ply2csv', help='Convert point cloud PLY to CSV')
    ply2csv_parser.add_argument('input_ply', help='Input point cloud PLY file')
    ply2csv_parser.add_argument('--output_csv', help='Output CSV filename (default: input_filename.csv)')
    
    # CSV to pointcloud command
    csv2ply_parser = subparsers.add_parser('csv2ply', help='Convert CSV to point cloud PLY')
    csv2ply_parser.add_argument('input_csv', help='Input CSV file')
    csv2ply_parser.add_argument('--output_ply', help='Output PLY filename (default: input_filename.ply)')
    csv2ply_parser.add_argument('--color_type', choices=['float', 'uchar'], default='uchar',
                               help='Color data type to use in PLY file')
    
    args = parser.parse_args()
    
    if args.command == 'ply2csv':
        output_path = convert_pointcloud_to_csv(args.input_ply, args.output_csv)
        print(f"Conversion complete: {output_path}")
    
    elif args.command == 'csv2ply':
        output_path = convert_csv_to_pointcloud(args.input_csv, args.output_ply, args.color_type)
        print(f"Conversion complete: {output_path}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
