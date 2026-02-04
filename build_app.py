#!/usr/bin/env python3
"""Build script to create macOS .app bundle."""

import subprocess
import sys
import os

def main():
    # Ensure we're in the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    print("Building Inclusive Design Wizard.app...")
    print("=" * 50)

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=Inclusive Design Wizard",
        "--windowed",  # Creates .app bundle, no terminal window
        "--onedir",    # Creates a directory with dependencies
        "--noconfirm", # Replace existing build
        "--clean",     # Clean cache before building

        # Add all necessary data
        "--add-data=config:config",
        "--add-data=prompts:prompts",
        "--add-data=core:core",
        "--add-data=ui:ui",

        # Hidden imports that PyInstaller might miss
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=sqlalchemy.dialects.sqlite",
        "--hidden-import=bcrypt",
        "--hidden-import=aiohttp",
        "--hidden-import=docx",

        # macOS specific
        "--osx-bundle-identifier=com.inclusivedesign.wizard",

        # Entry point
        "main.py"
    ]

    print("Running PyInstaller...")
    result = subprocess.run(cmd, cwd=project_dir)

    if result.returncode == 0:
        print()
        print("=" * 50)
        print("Build successful!")
        print()
        print("Your app is at:")
        print(f"  {project_dir}/dist/Inclusive Design Wizard.app")
        print()
        print("To install, run:")
        print('  cp -r "dist/Inclusive Design Wizard.app" /Applications/')
        print()
        print("Or drag the .app to your Applications folder in Finder.")
    else:
        print("Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
