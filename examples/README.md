# Sample Code for 3DGS Editor

This folder contains sample code for editing 3D Gaussian Splatting format data using the included sample "Haniwa.ply" or your own files.

## Sample Visualizations

![Haniwa model imported into Scaniverse](https://raw.githubusercontent.com/404background/3dgs-edit-tools/main/images/haniwa.png)
*Original 3D Gaussian Splatting visualization of the Haniwa model in Supersplat viewer*

![Haniwa point cloud visualization in CloudCompare](https://raw.githubusercontent.com/404background/3dgs-edit-tools/main/images/haniwa_pointcloud.png)
*Point cloud conversion of the Haniwa model visualized in CloudCompare*

![Haniwa mesh conversion example](https://raw.githubusercontent.com/404background/3dgs-edit-tools/main/images/haniwa_mesh.png)
*Mesh conversion result using the hybrid method with ultra quality settings*

All sample outputs have been confirmed to work with Supersplat viewer (3DGS) and CloudCompare (point clouds). Point cloud outputs have been extensively tested in CloudCompare for proper structure, color representation, and export compatibility. Mesh outputs have been verified with Blender to confirm proper mesh topology, material support, and visualization compatibility. For mesh conversion, parameter adjustment is crucial for creating smooth meshes with fewer holes - results depend significantly on the chosen reconstruction method and parameters.

## Command-Line Tools

The following executable tools are available in the `pyenv/Scripts` directory:

| Tool | Description |
|------|-------------|
| `compare-gs.exe` | Compare two 3D Gaussian Splatting files |
| `3dgs-to-mesh.exe` | Convert 3D Gaussian Splatting to mesh |
| `3dgs-to-csv.exe` | Convert 3D Gaussian Splatting to CSV |
| `csv-to-3dgs.exe` | Convert CSV to 3D Gaussian Splatting |
| `3dgs-to-pointcloud.exe` | Convert 3D Gaussian Splatting to point cloud |
| `pointcloud-to-3dgs.exe` | Convert point cloud to 3D Gaussian Splatting |
| `csv-to-pointcloud.exe` | Convert CSV to point cloud |
| `pointcloud-to-csv.exe` | Convert point cloud to CSV |
| `merge-gs.exe` | Merge multiple 3D Gaussian Splatting files |

### Example Usage

```bash
# Compare two 3D Gaussian Splatting files
compare-gs original.ply modified.ply --output-dir comparison_results

# Convert 3D Gaussian Splatting to mesh
3dgs-to-mesh input.ply --output output_mesh.obj --method hybrid --quality high

# Merge two 3D Gaussian Splatting files
merge-gs file1.ply file2.ply --output merged.ply --translate-x 0.1
```

## Sample Overview

1. **converter_sample.py** - Basic PLY⇔CSV conversion sample
   - Convert PLY format data to CSV
   - Slightly modify coordinate values
   - Convert edited data back to PLY

2. **transform_sample.py** - Sample for transforming the shape of a 3D Gaussian Splatting PLY file
   - Convert PLY format data to CSV
   - Scale 2x in the X-axis direction
   - Rotate 45 degrees around Z-axis
   - Convert transformed data back to PLY

3. **color_convert_sample.py** - Sample for changing colors to black
   - Convert PLY format data to CSV
   - Change all color values to black
   - Convert edited data back to PLY

4. **pointcloud_convert_sample.py** - Sample for converting to/from point cloud format
   - Convert 3D Gaussian Splatting to point cloud format
   - Convert point cloud to editable CSV
   - Edit CSV data (simulated without actual changes)
   - Convert edited CSV back to point cloud
   - Convert point cloud back to 3D Gaussian Splatting format

5. **mesh_convert_sample.py** - Sample for converting to mesh format
   - Convert 3D Gaussian Splatting PLY file to mesh format
   - Customize mesh generation parameters for quality and characteristics

6. **compare_gs_sample.py** - Sample for comparing two 3D Gaussian Splatting files
   - Compare original and transformed models
   - Generate detailed differences in CSV format
   - Visualize differences with color-coded points
   - Print summary of differences

7. **merge_gs_sample.py** - Sample for merging multiple 3DGS files
   - Create a transformed copy of an input 3DGS file
   - Apply translation to the copy (10cm on X-axis by default)
   - Merge the original and transformed files into a single 3DGS file

## How to Run the Samples

All samples accept a custom input PLY file using the `--input_ply` parameter. If not specified, the default "Haniwa.ply" will be used.

### 1. Basic Conversion Sample

```bash
python converter_sample.py [--input_ply YOUR_MODEL.ply]
```

Running this sample will generate the following files:
- `MODEL_converter.csv` - CSV file converted from the original PLY
- `MODEL_converter_modified.csv` - CSV file with slightly modified coordinates
- `MODEL_modified.ply` - PLY file restored from the edited data

### 2. Shape Transformation Sample

```bash
python transform_sample.py [--input_ply YOUR_MODEL.ply]
```

Running this sample will generate the following files:
- `MODEL.csv` - CSV file converted from the original PLY
- `MODEL_transformed.csv` - CSV file with transformed coordinates
- `MODEL_transformed.ply` - PLY file restored from the transformed data

### 3. Color Editing Sample

```bash
python color_convert_sample.py [--input_ply YOUR_MODEL.ply]
```

Running this sample will generate the following files (for example, with Haniwa.ply):
- `Haniwa.csv` - CSV file converted from the original PLY
- `Haniwa_black.csv` - CSV file with edited colors
- `Haniwa_black.ply` - PLY file restored from the edited data

### 4. Point Cloud Conversion Sample

```bash
python pointcloud_convert_sample.py [--input_ply YOUR_MODEL.ply] [--no_color]
```

Running this sample will generate the following files:
- `MODEL_pointcloud.ply` - Point cloud format file (with color information)
- `MODEL_pointcloud.csv` - CSV file converted from the point cloud
- `MODEL_edited.ply` - Edited point cloud from CSV file
- `MODEL_from_pointcloud.ply` - 3D Gaussian Splatting file converted from the point cloud

When using the `--no_color` option, the generated files will have different names:
- `MODEL_pointcloud_nocolor.ply` - Point cloud without color information
- `MODEL_pointcloud_nocolor.csv` - CSV file without color data
- `MODEL_edited_nocolor.ply` - Edited point cloud without color
- `MODEL_from_pointcloud_nocolor.ply` - 3D Gaussian Splatting file converted from colorless point cloud

### 5. Mesh Conversion Sample

```bash
python mesh_convert_sample.py [--input_ply YOUR_MODEL.ply] [--options]
```

Running this sample will convert the 3D Gaussian Splatting PLY file to a mesh format:
- `converted/MODEL_METHOD_QUALITY_PARAMS.obj` - Mesh format file with materials
- `converted/MODEL_METHOD_QUALITY_PARAMS.mtl` - Material file for the mesh
- `converted/MODEL_pointcloud.ply` - Intermediate point cloud file

### 6. File Comparison Sample

```bash
python compare_gs_sample.py
```

This sample compares the original PLY file with the transformed version created by `transform_sample.py`. You need to run `transform_sample.py` first to generate the comparison target.

Running this sample will generate the following files:
- `comparison_results/differences.csv` - Detailed information about all differences
- `comparison_results/diff_visualization.png` - 3D visualization showing points with differences

### 7. File Merging Sample

```bash
python merge_gs_sample.py [--input_ply YOUR_MODEL.ply] [--translation 0.2]
```

Running this sample will generate the following files:
- `converted/MODEL_transformed.ply` - A copy of the original model with X-axis translation
- `converted/MODEL_merged.ply` - Merged model containing both the original and transformed copy
- `converted/MODEL_merged_merged.csv` - Intermediate CSV file containing the combined data

The resulting merged PLY file will contain two copies of the model - the original one and a copy that has been moved by the specified translation distance (default: 10cm along X-axis). This demonstrates how multiple 3DGS objects can be combined into a single scene.

## Mesh Conversion Parameters

The `mesh_convert_sample.py` script and the `3dgs-to-mesh.exe` tool offer various parameters to control the quality and characteristics of the generated mesh:

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--output_format` | obj, ply, stl | obj | Output mesh file format |
| `--method` | poisson, ball_pivoting, alpha_shape, hybrid | hybrid | Mesh reconstruction method |
| `--quality` | low, normal, high, ultra | high | Reconstruction quality preset |
| `--smoothness` | 0.0-3.0 | 1.5 | Strength of mesh smoothing (higher = smoother) |
| `--fill_holes` | flag | off | Enable hole filling in the mesh |
| `--aggressive_holes` | flag | off | Use aggressive hole filling techniques |
| `--density` | 0.001-0.05 | 0.01 | Density threshold percentile for filtering (lower = more points) |
| `--neighbors` | 10-100 | 30 | Number of neighbors for normal estimation (higher = smoother surface) |
| `--super_smooth` | flag | off | Apply maximum smoothing (sets smoothness=3.0) |
| `--depth` | integer | 0 (auto) | Override default poisson reconstruction depth |
| `--scale` | float | 1.0 | Scale factor for the mesh |

### Mesh Reconstruction Methods

- **poisson**: Creates watertight meshes with smooth surfaces but may lose some detail. Good for objects with continuous surfaces.
- **ball_pivoting**: Preserves original points well but may create holes. Good for flat surfaces and detailed models.
- **alpha_shape**: Similar to ball pivoting but with better hole handling. Good for maintaining shape boundaries.
- **hybrid**: Combines multiple methods for optimal results. Recommended for most 3D Gaussian Splatting models.

### Quality Presets

The quality presets affect multiple parameters including poisson depth, normal estimation quality, and mesh refinement:

- **low**: Fastest processing with basic quality (Poisson depth ~8)
- **normal**: Balanced between speed and quality (Poisson depth ~9)
- **high**: Detailed reconstruction with good smoothing (Poisson depth ~10)
- **ultra**: Maximum detail preservation with enhanced processing (Poisson depth ~11-12)

### Optimization Tips

For smoother mesh generation with reduced surface irregularities:

1. **For maximum smoothness**: Use `--super_smooth --method hybrid --quality ultra --fill_holes --aggressive_holes --neighbors 60 --density 0.005`
2. **For balance between detail and smoothness**: Use `--smoothness 2.0 --method hybrid --quality high --neighbors 40`
3. **For preserving fine details**: Use `--method ball_pivoting --quality high --neighbors 20 --smoothness 0.5`

## Direct Mesh Conversion

Using the new direct mesh conversion functionality (`gs_to_mesh.py`), you can now convert 3DGS files to mesh formats in a single step:

```bash
3dgs-to-mesh input.ply --output output_mesh.obj --method hybrid --quality ultra --fill_holes
```

This direct conversion internally uses the same two-step process (3DGS→point cloud→mesh) but provides a simplified interface with all the same mesh generation options.
