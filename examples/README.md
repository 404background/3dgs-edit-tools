# Sample Code for 3DGS Editor

This folder contains sample code for editing 3D Gaussian Splatting format data. The sample data "Haniwa.ply" is included for these examples, but you can use any 3D Gaussian Splatting PLY file.

![Haniwa model imported into Scaniverse](https://raw.githubusercontent.com/404background/3dgs-edit-tools/main/images/haniwa.png)

All sample output files have been verified to be readable and display correctly in the Supersplat viewer for 3D Gaussian Splatting files and CloudCompare for point cloud files. 

![Haniwa point cloud visualization in CloudCompare](https://raw.githubusercontent.com/404background/3dgs-edit-tools/main/images/haniwa_pointcloud.png)

Each sample's output has been confirmed to load without errors, ensuring proper compatibility with both formats.

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
python pointcloud_convert_sample.py [--input_ply YOUR_MODEL.ply]
```

Running this sample will generate the following files:
- `MODEL_pointcloud.ply` - Point cloud format file
- `MODEL_pointcloud.csv` - CSV file converted from the point cloud
- `MODEL_from_csv.ply` - Restored point cloud from edited CSV
- `MODEL_from_pointcloud.ply` - 3D Gaussian Splatting file converted from the point cloud
