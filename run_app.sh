#!/bin/bash
# Script to install and run Inclusive Design Wizard

# Remove old installation
rm -rf "/Applications/Inclusive Design Wizard.app"

# Copy new app
cp -r "/Users/roccocatrone/inclusive-design-wizard/dist/Inclusive Design Wizard.app" /Applications/

# Remove quarantine
xattr -cr "/Applications/Inclusive Design Wizard.app"

# Open the app
open "/Applications/Inclusive Design Wizard.app"
