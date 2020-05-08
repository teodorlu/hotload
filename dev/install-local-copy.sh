#!/bin/bash
DIR="$(git rev-parse --show-toplevel)"
mkdir -p ~/.local/bin
rm -f ~/.local/bin/hotload
cp "$DIR/hotload.py" ~/.local/bin/hotload
chmod +x ~/.local/bin/hotload
