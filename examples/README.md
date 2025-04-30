# Sample Code for 3DGS Editor

This folder contains sample code for editing 3D Gaussian Splatting format data. The sample data "Haniwa.ply" is used for these examples.

![Haniwa model imported into Scaniverse](../images/haniwa.png)

All sample output files have been verified to be readable and display correctly in the Supersplat viewer. Each sample's output has been confirmed to load without errors in Supersplat, ensuring proper compatibility with the 3D Gaussian Splatting format.

## Sample Overview

1. **transform_sample.py** - Sample for transforming the shape of Haniwa.ply
   - Convert PLY format data to CSV
   - Scale 2x in the X-axis direction
   - Rotate 45 degrees around Z-axis
   - Convert transformed data back to PLY

2. **converter_sample.py** - Basic PLY⇔CSV conversion sample
   - Convert PLY format data to CSV
   - Slightly modify coordinate values
   - Convert edited data back to PLY

3. **color_convert_sample.py** - Sample for changing colors to black
   - Convert PLY format data to CSV
   - Change all color values to black
   - Convert edited data back to PLY

## How to Run the Samples

### 1. Color Editing Sample

```bash
python color_convert_sample.py
```

Running this sample will generate the following files:
- `Haniwa.csv` - CSV file converted from the original PLY
- `Haniwa_footer.tmp` - Footer data needed for restoration
- `Haniwa_black.csv` - CSV file with edited colors
- `Haniwa_black.ply` - PLY file restored from the edited data

### 2. Shape Transformation Sample

```bash
python transform_sample.py
```

Running this sample will generate the following files:
- `Haniwa.csv` - CSV file converted from the original PLY
- `Haniwa_footer.tmp` - Footer data needed for restoration
- `Haniwa_transformed.csv` - CSV file with transformed coordinates
- `Haniwa_transformed.ply` - PLY file restored from the transformed data

### 3. Basic Conversion Sample

```bash
python converter_sample.py
```

Running this sample will generate the following files:
- `Haniwa.csv` - CSV file converted from the original PLY
- `Haniwa_footer.tmp` - Footer data needed for restoration
- `Haniwa_modified.csv` - CSV file with slightly modified coordinates
- `Haniwa_modified.ply` - PLY file restored from the edited data
