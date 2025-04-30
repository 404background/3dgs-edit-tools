# 3DGS Editor

A Python library to convert 3D Gaussian Splatting (3DGS) format data to CSV format, edit it, and convert it back to 3DGS format.

## Features

- Convert 3DGS format (PLY) data to CSV format
- Convert CSV format data to 3DGS format (PLY)
- Batch processing for converting multiple files
- Verified compatibility with Supersplat for visualization

## Installation

Clone this repository:

```bash
git clone https://github.com/yourname/3dgs-edit-tools.git
cd 3dgs-edit-tools
```

## Usage

### As a Library

```python
from src import convert_3dgs_to_csv, convert_csv_to_3dgs

# Convert PLY file to CSV
csv_path, footer_path = convert_3dgs_to_csv('model.ply')

# Write your code to edit the CSV file here
# ...

# Convert edited CSV back to PLY
restored_ply = convert_csv_to_3dgs(csv_path, footer_path)
```

### From Command Line

Convert PLY to CSV:

```bash
python src/gs_to_csv.py input.ply --output_csv output.csv --footer footer.tmp
```

Convert CSV to PLY:

```bash
python src/csv_to_gs.py input.csv footer.tmp --output_ply output.ply
```

### Sample Code

Sample code is available in the `examples` folder. See `examples/README.md` for details.

## API Reference

### convert_3dgs_to_csv(ply_filename, csv_filename=None, footer_filename=None)

Converts 3DGS format (PLY) data to CSV format.

**Arguments**:
- `ply_filename` (str): Path to the input PLY file
- `csv_filename` (str, optional): Path to the output CSV file. If not specified, it's automatically generated from the input filename
- `footer_filename` (str, optional): Path to save the footer data. If not specified, it's automatically generated from the input filename

**Returns**:
- tuple: (csv_filename, footer_filename) - Paths of the generated files

### convert_csv_to_3dgs(csv_filename, footer_filename, output_ply_filename=None)

Converts CSV format data to 3DGS format (PLY).

**Arguments**:
- `csv_filename` (str): Path to the input CSV file
- `footer_filename` (str): Path to the file containing footer data
- `output_ply_filename` (str, optional): Path to the output PLY file. If not specified, it's automatically generated from the input filename

**Returns**:
- str: Path of the generated PLY file

## License

This project is released under the MIT License. See LICENSE file for details.
