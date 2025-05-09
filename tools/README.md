# 3D Gaussian Splatting Tools

This folder contains tools for working with 3D Gaussian Splatting (3DGS) data.

## build_package.py - Package Build and Publishing Tool

This tool provides utilities for building and publishing the 3DGS Editor package. It offers all the functionality needed to publish the package to PyPI.

### Key Features

- Package building (source distribution and wheel packages)
- Publishing to TestPyPI (for testing)
- Publishing to production PyPI
- Cleanup of build directories

### Usage

```bash
# Build the package
python -m tools.build_package build

# Publish to TestPyPI (for testing)
python -m tools.build_package publish

# Publish to production PyPI
python -m tools.build_package publish-prod

# Clean build directories
python -m tools.build_package clean
```

For detailed instructions, refer to `PUBLISHING.md`.

## compare_gs.py - 3DGS Comparison Tool

This tool performs detailed analysis of differences between two 3DGS PLY files. By converting to CSV format, it enables accurate identification of differences in the data.

### Key Features

- Detects differences between two PLY files
- Detailed analysis of positions, colors, and other properties
- Visualization of differences (3D plot)
- Exports detailed difference data as CSV

### Usage

```bash
python -m tools.compare_gs <PLY_FILE_1> <PLY_FILE_2> [options]
```

Or, from the project root directory:

```bash
python -m tools.compare_gs examples\Haniwa.ply examples\converted\Haniwa_from_pointcloud.ply --output-dir examples\converted\comparison
```

### Options

- `--output-dir`, `-o`: Specify directory to save output files
- `--tolerance`, `-t`: Tolerance for floating-point comparison (default: 1e-6)
- `--no-visualization`: Skip visualization of differences

### Output Examples

```
==== 3DGS File Comparison Results ====
File 1: examples\Haniwa.ply
File 2: examples\converted\Haniwa_from_pointcloud.ply

Total rows compared: 56639
Rows with differences: 0

Result: The files are identical (within the specified tolerance)
```

Or when differences exist:

```
==== 3DGS File Comparison Results ====
File 1: examples\Haniwa.ply
File 2: examples\converted\Haniwa_from_pointcloud.ply

Total rows compared: 56639
Rows with differences: 56639
Column differences summary:
  f_dc_0: 56639 differences
  f_dc_1: 56639 differences
  f_dc_2: 56638 differences

Detailed differences saved to: examples\converted\comparison\differences.csv

Result: The files are different
```

This tool helps you identify and fix issues that occur during PLY file conversion or editing processes.

## Module Organization Structure

The project is organized into modular components, each handling specific conversion and processing tasks:

1. **Core File Conversion**: 
   - `gs_to_csv.py` - 3DGS to CSV conversion
   - `csv_to_gs.py` - CSV to 3DGS conversion

2. **Point Cloud Operations**:
   - `gs_to_pointcloud.py` - 3DGS to point cloud conversion
   - `pointcloud_to_gs.py` - Point cloud to 3DGS conversion
   - `pointcloud_to_csv.py` - Point cloud to/from CSV conversion

3. **Mesh Generation**:
   - `pointcloud_to_mesh.py` - Point cloud to mesh conversion
   - `gs_to_mesh.py` - Direct 3DGS to mesh conversion

4. **Analysis & Utilities**:
   - `compare_gs.py` - File comparison for 3DGS files
   - `color_utils.py` - Color processing utilities
   - `merge_gs.py` - File merging and transformation

### Development Guidelines

When extending or modifying these tools:

1. Maintain the modular architecture to keep code organized
2. Follow the existing pattern for command-line interfaces
3. Update documentation and examples when adding new features
4. Ensure proper error handling for all conversion operations
5. Add new testing code to verify functionality

### Package Build & Publish Process

To build and publish a new version of the package:

1. Update version number in `setup.py`
2. Run the build process: `python -m tools.build_package build`
3. Test locally with the development install: `pip install -e .`
4. Test with TestPyPI: `python -m tools.build_package publish`
5. Publish to production PyPI: `python -m tools.build_package publish-prod`

For more detailed instructions, see `PUBLISHING.md`.
