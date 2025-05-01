import struct
import csv
import os
import numpy as np
from . import color_utils


def convert_csv_to_3dgs(csv_filename, footer_filename=None, output_ply_filename=None):
    """
    Convert CSV format data to 3D Gaussian Splatting format (.ply)
    
    Args:
        csv_filename (str): Path to the input CSV file
        footer_filename (str, optional): Path to the footer file (deprecated, not used)
        output_ply_filename (str, optional): Path to the output PLY file. If not specified, it's automatically generated from the input filename
        
    Returns:
        str: Path of the generated PLY file
    """
    # Automatically generate output filename
    if output_ply_filename is None:
        base_name = os.path.splitext(csv_filename)[0]
        output_ply_filename = f"{base_name}_restored.ply"
    
    # Note: footer_filename is ignored as footer data is no longer used
    if footer_filename:
        print(f"Note: Footer file {footer_filename} is ignored (footers no longer used)")
        
    # Load CSV data
    with open(csv_filename, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        data = [row for row in reader]

    vertex_count = len(data)
    num_floats = len(header)

    # Detect color-related properties
    r_idx, g_idx, b_idx, is_sh_color = color_utils.detect_color_properties(header)
    
    # If color-related properties are detected
    if is_sh_color:
        color_props = [header[i] for i in [r_idx, g_idx, b_idx]]
        print(f"Detected spherical harmonic color coefficients: {color_props}")
        
        # Analyze color values in the CSV
        color_values = []
        for row in data:
            try:
                color_values.append([float(row[i]) for i in [r_idx, g_idx, b_idx]])
            except (ValueError, IndexError):
                # Skip processing if there are conversion errors or missing values
                continue
        
        if color_values:
            # Get the range of color values
            min_val, max_val, is_signed = color_utils.get_color_value_range(color_values)
            print(f"Current color range: {min_val} to {max_val}, signed: {is_signed}")
            
            # If current values are in standard color range (0-1 or 0-255), adjust for SH coefficients
            if max_val <= 1.0 and min_val >= 0:
                print("Values appear to be in 0-1 range, adjusting for SH coefficients...")
                
                # Convert color values in each row for SH coefficients
                for row in data:
                    # Convert from string to numeric and process as array
                    try:
                        color = np.array([[float(row[r_idx]), float(row[g_idx]), float(row[b_idx])]])
                        
                        # Convert from standard color to SH coefficients
                        sh_colors = color_utils.convert_standard_to_sh_color(color)
                        
                        # Put converted values back into the original data
                        row[r_idx] = str(sh_colors[0][0])
                        row[g_idx] = str(sh_colors[0][1])
                        row[b_idx] = str(sh_colors[0][2])
                    except (ValueError, IndexError) as e:
                        print(f"WARNING: Error converting color value: {e}")
            
            elif max_val <= 255.0 and min_val >= 0:
                print("Values appear to be in 0-255 range, normalizing and adjusting for SH coefficients...")
                
                # Normalize from 0-255 range to 0-1 and then convert to SH coefficients
                for row in data:
                    try:
                        color = np.array([[float(row[r_idx]), float(row[g_idx]), float(row[b_idx])]])
                        
                        # Normalize colors and convert to SH coefficients
                        normalized = color / 255.0
                        sh_colors = color_utils.convert_standard_to_sh_color(normalized)
                        
                        # Put converted values back into the original data
                        row[r_idx] = str(sh_colors[0][0])
                        row[g_idx] = str(sh_colors[0][1])
                        row[b_idx] = str(sh_colors[0][2])
                    except (ValueError, IndexError) as e:
                        print(f"WARNING: Error converting color value: {e}")

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
            try:
                float_values = [float(v) for v in row]
                f.write(struct.pack("<" + "f" * num_floats, *float_values))
            except (ValueError, struct.error) as e:
                print(f"WARNING: Error writing vertex data: {e}")
                # Fill with zeros if an error occurs
                f.write(struct.pack("<" + "f" * num_floats, *[0.0] * num_floats))

    print(f"Successfully converted CSV data to 3D Gaussian Splatting format ({vertex_count} vertices)")
    return output_ply_filename


def main():
    """Entry point for command-line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert CSV format data to 3D Gaussian Splatting format')
    parser.add_argument('input_csv', help='Input CSV file')
    parser.add_argument('--footer', help='Footer filename (deprecated, not used)')
    parser.add_argument('--output_ply', help='Output PLY filename (default: input_filename_restored.ply)')
    
    args = parser.parse_args()
    
    output_path = convert_csv_to_3dgs(
        args.input_csv,
        args.footer,
        args.output_ply
    )
    
    print(f"Restoration complete: {output_path}")


if __name__ == "__main__":
    main()
