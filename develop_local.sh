DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
mkdir -p ~/.local/bin
ln -sf "$DIR/hotload.py" ~/.local/bin/hotload
chmod +x ~/.local/bin/hotload