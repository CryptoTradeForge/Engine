#!/bin/bash

set -e

echo "Downloading TA-Lib source..."
wget https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz

echo "Extracting TA-Lib source..."
tar -xzf ta-lib-0.6.4-src.tar.gz

cd ta-lib-0.6.4

echo "Configuring, building, and installing TA-Lib..."
./configure
make
make install

cd ..

echo "Installing Python TA-Lib package..."
pip install ta-lib==0.6.1

echo "Cleaning up..."
rm -rf ta-lib-0.6.4 ta-lib-0.6.4-src.tar.gz

echo "TA-Lib installation completed!"
