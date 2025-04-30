# 3D Gaussian Splatting Tools

This folder contains tools for working with 3D Gaussian Splatting (3DGS) data.

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
