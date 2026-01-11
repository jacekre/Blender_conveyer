#!/bin/bash
# Quick test render - only 3 frames

echo "Starting quick test render (3 frames only)..."
echo ""

if ! command -v blender &> /dev/null; then
    echo "ERROR: Blender not found in PATH"
    exit 1
fi

blender --background --python scripts/test_render.py

echo ""
echo "Test complete! Check renders/test folder."
