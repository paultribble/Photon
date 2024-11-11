#!/bin/bash

# Update package lists
sudo apt update

# Define packages
packages=(
    "python3-tk"         # tkinter (import tkinter as tk)
    "python3-pip"        # pip for installing Python packages
    "python3-psycopg2"   # psycopg2 for PostgreSQL (import psycopg2)
    "python3-pil"        # PIL (Python Imaging Library) (import PIL)
)

# Install packages
for package in "${packages[@]}"; do
    if ! dpkg -s "$package" >/dev/null 2>&1; then
        echo "Installing $package..."
        sudo apt install -y "$package"
    else
        echo "$package is already installed."
    fi
done

# Install pynput via pip
if ! python3 -c "import pynput" &> /dev/null; then
    echo "Installing pynput..."
    python3 -m pip install pynput
else
    echo "pynput is already installed."
fi

# Clean up
sudo apt autoremove -y

echo "All packages installed or already present."
