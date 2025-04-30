import struct
import csv
import os


def convert_csv_to_3dgs(csv_filename, footer_filename, output_ply_filename=None):
    """
    Convert CSV format data to 3D Gaussian Splatting format (.ply)
    
    Args:
        csv_filename (str): Path to the input CSV file
        footer_filename (str): Path to the file containing footer data
        output_ply_filename (str, optional): Path to the output PLY file. If not specified, it's automatically generated from the input filename
        
    Returns:
        str: Path of the generated PLY file
    """
    # Automatically generate output filename
    if output_ply_filename is None:
        base_name = os.path.splitext(csv_filename)[0]
        output_ply_filename = f"{base_name}_restored.ply"
    
    # Load CSV data
    with open(csv_filename, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        data = [row for row in reader]

    vertex_count = len(data)
    num_floats = len(header)

    # Generate header
    ply_header = """ply
format binary_little_endian 1.0
element vertex {vertex_count}
""" + "\n".join([f"property float {name}" for name in header]) + """
end_header
"""

    final_header = ply_header.format(vertex_count=vertex_count)

    # Write to PLY file
    with open(output_ply_filename, "wb") as f:
        # Header
        f.write(final_header.encode("ascii"))
        
        # Binary data
        for row in data:
            float_values = [float(v) for v in row]
            f.write(struct.pack("<" + "f" * num_floats, *float_values))
        
        # Footer
        with open(footer_filename, "rb") as footer_file:
            f.write(footer_file.read())

    return output_ply_filename


def main():
    """Entry point for command-line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert CSV format data to 3D Gaussian Splatting format')
    parser.add_argument('input_csv', help='Input CSV file')
    parser.add_argument('footer_file', help='File containing footer data')
    parser.add_argument('--output_ply', help='Output PLY filename (default: input_filename_restored.ply)')
    
    args = parser.parse_args()
    
    output_path = convert_csv_to_3dgs(
        args.input_csv, 
        args.footer_file, 
        args.output_ply
    )
    
    print(f"Restoration complete: {output_path}")


if __name__ == "__main__":
    main()
