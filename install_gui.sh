#!/bin/sh

# Check if virtualenv is installed
if ! command -v virtualenv &> /dev/null
then
  echo "virtualenv is not installed, install using your package manager of choice, pip or pipx"
  exit 1
fi

# Create a temporary virtualenv (has to be python 3.10 or python 3.11)
virtualenv tmpvenv --python=python3.11

# Activate the temporary virtualenv
source tmpvenv/bin/activate

# Make sure pip is up to date
pip install --upgrade pip

# Install dependencies
pip install .

# Make sure pyinstaller is installed
pip install pyinstaller

# Build
pyinstaller --onedir --clean --windowed gui.py

# Deactivate the temporary virtualenv
deactivate

# Remove the temporary virtualenv
rm -rf tmpvenv
