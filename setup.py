from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="3dgs-edit-tools",
    version="0.2.0",
    author="404background",
    author_email="404background@gmail.com",
    description="A Python library to convert, edit, and manage 3D Gaussian Splatting data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/404background/3dgs-edit-tools",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "3dgs-to-csv=src.gs_to_csv:main",
            "csv-to-3dgs=src.csv_to_gs:main",
            "3dgs-to-pointcloud=src.gs_to_pointcloud:main",
            "pointcloud-to-3dgs=src.pointcloud_to_gs:main",
            "pointcloud-to-csv=src.pointcloud_to_csv:main",
            "csv-to-pointcloud=src.pointcloud_to_csv:main_csv_to_ply",
            "compare-gs=tools.compare_gs:main",
            "3dgs-to-mesh=src.pointcloud_to_mesh:main_3dgs_to_mesh",
            "merge-gs=src.merge_gs:main",
        ],
    },
    install_requires=[
        "numpy",
        "open3d",
    ],
    extras_require={
        "tools": ["pandas", "matplotlib"],
    },
)