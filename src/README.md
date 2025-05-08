# 3DGS Editor Source Code Structure

This directory (`src/`) contains the main source code for editing and converting 3D Gaussian Splatting (3DGS) data. Each file is responsible for specific functionality and is designed in a modular way.

## File Structure and Feature Overview

| Filename | Main Function | Key Functions |
|------------|---------|---------|
| `__init__.py` | Package initialization and API definition | - |
| `gs_to_csv.py` | Convert 3DGS files (PLY) to CSV format | `convert_3dgs_to_csv()` |
| `csv_to_gs.py` | Convert CSV format to 3DGS files (PLY) | `convert_csv_to_3dgs()` |
| `gs_to_pointcloud.py` | Convert 3DGS files to standard point cloud format | `convert_3dgs_to_pointcloud()` |
| `pointcloud_to_gs.py` | Convert point cloud to 3DGS format | `convert_pointcloud_to_3dgs()` |
| `pointcloud_to_csv.py` | Convert between point cloud and CSV formats | `convert_pointcloud_to_csv()`, `convert_csv_to_pointcloud()` |
| `pointcloud_to_mesh.py` | Convert point cloud to mesh format | `convert_pointcloud_to_mesh()`, `convert_3dgs_to_mesh()` |
| `compare_gs.py` | Compare two 3DGS files and analyze differences | `compare_3dgs_files()` |
| `color_utils.py` | Utility functions for color information processing | `detect_color_properties()`, `convert_standard_to_sh_color()` |

## Detailed Explanation

### Basic Data Conversion Flow

The workflow for editing 3DGS data is as follows:

1. **3DGS → CSV conversion**: Convert 3D Gaussian Splatting format (PLY) to CSV format
2. **CSV editing**: Edit the CSV file in a spreadsheet or any editor
3. **CSV → 3DGS conversion**: Convert the edited CSV file back to 3DGS format

### Main Module Details

#### gs_to_csv.py

Converts 3DGS format (PLY) files to CSV format. This makes the data human-readable and editable. All information including color data, coordinates, and ellipsoid orientations is preserved.

#### csv_to_gs.py

Converts CSV files back to 3DGS format (PLY). Used to restore edited data to the original format.

#### gs_to_pointcloud.py

Converts 3DGS files to standard point cloud format. This allows 3DGS data to be handled with standard tools like CloudCompare.

#### pointcloud_to_gs.py

Converts point cloud data to 3DGS format. Used to display and utilize existing point cloud data as Gaussian Splatting.

#### pointcloud_to_csv.py

Performs conversion between point cloud and CSV formats. Enables simple editing of point cloud data.

#### pointcloud_to_mesh.py

Provides conversion from point cloud to mesh formats (OBJ, PLY, etc.). This module implements multiple mesh reconstruction algorithms (Poisson, Ball Pivoting, Alpha Shape, Hybrid, etc.).

#### compare_gs.py

Compares two 3DGS files and analyzes differences in detail. Helpful for verifying data consistency after conversion or editing.

#### color_utils.py

Provides utility functions for color information processing. Includes functionality for detecting and converting Spherical Harmonics color format, properly handling color information in 3DGS.

## Command Line Execution

Each module is equipped with a command line interface and is provided as the following executable files (in the `pyenv/Scripts/` directory):

- `3dgs-to-csv.exe` - Convert 3DGS file to CSV
- `csv-to-3dgs.exe` - Convert CSV file to 3DGS
- `3dgs-to-pointcloud.exe` - Convert 3DGS file to point cloud
- `pointcloud-to-3dgs.exe` - Convert point cloud to 3DGS
- `pointcloud-to-csv.exe` - Convert point cloud to CSV
- `csv-to-pointcloud.exe` - Convert CSV file to point cloud
- `compare-gs.exe` - Compare two 3DGS files
- `3dgs-to-mesh.exe` - Convert 3DGS file to mesh

For detailed usage instructions, refer to the `--help` option for each command line tool.