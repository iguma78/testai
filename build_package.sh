#!/bin/bash
# Simple script to build the TestAI SDK package

echo "Building TestAI SDK package..."

# Clean up any previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m pip install --upgrade build
python -m build

echo "Build complete! Distribution files are in the 'dist' directory."
echo ""
echo "To install the package locally for testing, run:"
echo "pip install -e ."
echo ""
echo "To publish to PyPI, run:"
echo "python -m pip install --upgrade twine"
echo "python -m twine upload dist/*"
