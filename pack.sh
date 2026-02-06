#!/bin/bash

ZIP_FILE="whatsapp-scraper.zip"

# Remove existing zip file if it exists
if [ -f "$ZIP_FILE" ]; then
    echo "Removing existing $ZIP_FILE..."
    rm "$ZIP_FILE"
fi

echo "Creating $ZIP_FILE..."

# Zip the extension files
zip -r "$ZIP_FILE" . -x "*.git*" "*.DS_Store" "*_metadata*" "pack.sh"

echo "Done! $ZIP_FILE created."
