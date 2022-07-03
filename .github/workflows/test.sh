#!/bin/bash
set -e

cat <<EOF >lib.py
x = 3
y = 4
print("Result: {}".format(x*x + y*y))
EOF
touch -t 200711121015 lib.py

echo lib.py | python3 -u ./hotload.py lib.py > output &
pid="$!"

sleep 0.1
sed -i.bak "s/x = ./x = 4/" lib.py
sleep 0.1
kill "$pid"

strings output | grep -o -m1 'Successfully reloaded lib'
strings output | grep -o -m1 'Result: 25$'
strings output | grep -o -m1 'Result: 32$'

