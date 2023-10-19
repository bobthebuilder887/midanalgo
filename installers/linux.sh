#!/bin/sh
# Make sure pip is up to date
pip install --upgrade pip

# Make sure pyinstaller is installed
pip install pyinstaller

# Build
pyinstaller --onedir --clean --windowed gui.py
