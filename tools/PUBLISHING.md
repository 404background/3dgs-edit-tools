# Package Publishing Guide

This document explains how to build and publish the 3DGS Editor package to PyPI.

## Prerequisites

To publish the package, you need:

1. A PyPI account (create one at [https://pypi.org/account/register/](https://pypi.org/account/register/))
2. The following Python packages (will be installed automatically):
   - build
   - twine
   - tomli (included in standard library for some Python versions)

## Publishing Commands

This repository includes helper scripts for building and publishing the package. You can run the following commands from the package's root directory:

### Building the Package

```bash
python -m tools.build_package build
```

This command will:
1. Clean up existing build directories
2. Create source distribution and wheel packages
3. Store the created files in the `dist/` directory

### Publishing to TestPyPI (Recommended Testing Procedure)

It is recommended to test your package on TestPyPI before publishing to production PyPI:

```bash
python -m tools.build_package publish
```

After successful publication, you can install from TestPyPI using:

```bash
pip install --index-url https://test.pypi.org/simple/ 3dgs-editor
```

### Publishing to Production PyPI

Once all tests are complete, you can publish to production PyPI:

```bash
python -m tools.build_package publish-prod
```

After publication, anyone worldwide can install your package using:

```bash
pip install 3dgs-editor
```

## Package Version Management

Package versions are managed in the `pyproject.toml` file. Update the version number in this file before publishing a new version:

```toml
[project]
name = "3dgs-editor"
version = "0.1.0"  # Update this value
```

It is recommended to use semantic versioning:
- Patch release (bug fixes): 0.1.0 → 0.1.1
- Minor release (backward-compatible feature additions): 0.1.1 → 0.2.0
- Major release (backward-incompatible changes): 0.2.0 → 1.0.0

## Packaging Best Practices

1. Always verify the metadata in `pyproject.toml` before publishing (name, description, URLs, etc.)
2. Ensure `README.md` is up-to-date
3. Make sure installation instructions and command-line usage are clearly documented
4. Consider maintaining a `CHANGELOG.md` to track version changes

## Troubleshooting

### Common Issues

- **"Filename has already been used" error**: You're trying to upload the same version again. Update the version number in `pyproject.toml`.
- **Authentication errors**: Ensure your `~/.pypirc` file is properly configured, or enter your username and password at the twine authentication prompt.
- **Package validation errors**: You might be missing required files (like `README.md`).

### Other Problems

For other issues, refer to the [Python Packaging User Guide](https://packaging.python.org/) or create an issue on GitHub.