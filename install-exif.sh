#!/usr/bin/env bash
set -euo pipefail

TARGET_VERSION="13.30"
TEMP_DIR="$(mktemp -d)"
INSTALL_PREFIX="/usr/local"

echo "Installing ExifTool version ${TARGET_VERSION}..."

cd "$TEMP_DIR"

# Download the specified version tarball
TARBALL="Image-ExifTool-${TARGET_VERSION}.tar.gz"
URL="https://sourceforge.net/projects/exiftool/files/${TARBALL}/download" 


echo "Downloading ${TARBALL}..."
wget -q "$URL" -O "$TARBALL" -O ${TARBALL}

echo "Extracting..."
tar xzf "$TARBALL"
cd "Image-ExifTool-${TARGET_VERSION}"

echo "Building..."
perl Makefile.PL
make

echo "Installing..."
sudo make install

echo "Cleaning up..."
cd /
rm -rf "$TEMP_DIR"

echo "Installation complete. Verifying version..."
INSTALLED="$(exiftool -ver)"
echo "Installed ExifTool version: $INSTALLED"

if [[ "$INSTALLED" == "$TARGET_VERSION" ]]; then
    echo "Success: Version properly installed."
else
    echo "Warning: Expected version ${TARGET_VERSION}, but found ${INSTALLED}."
fi
