#!/bin/bash
# Shell script to run Blender conveyor simulation
# Make sure Blender is in your PATH

echo "Starting Blender Conveyor Simulation..."
echo ""

# Check if blender is in PATH
if ! command -v blender &> /dev/null; then
    echo "ERROR: Blender not found in PATH"
    echo "Please install Blender or add it to your PATH"
    exit 1
fi

# Run the simulation
blender --background --python scripts/main.py

echo ""
echo "Simulation complete! Check the renders folder."
