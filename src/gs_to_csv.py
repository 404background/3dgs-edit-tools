import struct
import csv
import os


def convert_3dgs_to_csv(ply_filename, csv_filename=None, footer_filename=None):
    """
    Convert 3D Gaussian Splatting format (.ply) data to CSV format
    
    Args:
        ply_filename (str): Path to the input PLY file
        csv_filename (str, optional): Path to the output CSV file. If not specified, it's automatically generated from the input filename
        footer_filename (str, optional): Path to save the footer data. If not specified, it's automatically generated from the input filename
        
    Returns:
        tuple: (csv_filename, footer_filename) - Paths of the generated files
    """
    # Automatically generate output filename
    if csv_filename is None:
        base_name = os.path.splitext(ply_filename)[0]
        csv_filename = f"{base_name}.csv"
    
    if footer_filename is None:
        base_name = os.path.splitext(ply_filename)[0]
        footer_filename = f"{base_name}_footer.tmp"

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

    # Split binary data and footer
    data_section = content[data_start:data_end]
    footer_section = content[data_end:]

    # Convert binary data to float
    data = []
    for i in range(vertex_count):
        start = i * num_floats * 4
        end = start + num_floats * 4
        floats = struct.unpack("<" + "f" * num_floats, data_section[start:end])
        data.append(floats)

    # Save to CSV
    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(properties)
        writer.writerows(data)

    # Save footer
    with open(footer_filename, "wb") as footer_file:
        footer_file.write(footer_section)
    
    return csv_filename, footer_filename


def main():
    """Entry point for command-line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert 3D Gaussian Splatting data to CSV format')
    parser.add_argument('input_ply', help='Input PLY file')
    parser.add_argument('--output_csv', help='Output CSV filename (default: input_filename.csv)')
    parser.add_argument('--footer', help='Footer data output path (default: input_filename_footer.tmp)')
    
    args = parser.parse_args()
    
    csv_path, footer_path = convert_3dgs_to_csv(
        args.input_ply, 
        args.output_csv, 
        args.footer
    )
    
    print(f"Conversion complete: CSV → {csv_path} / Footer → {footer_path}")


if __name__ == "__main__":
    main()
