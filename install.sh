#!/bin/bash

set -e

# Ensure we've got our folder and remove previous versions
mkdir -p ~/.local/bin
rm -f ~/.local/bin/hotload

# Install latest version
wget https://raw.githubusercontent.com/teodorlu/hotload/master/hotload.py -O ~/.local/bin/hotload
chmod +x ~/.local/bin/hotload
