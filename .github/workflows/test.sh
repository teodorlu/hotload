#!/bin/bash
set -e

cat <<EOF >mymath.py
def f(x,y):
    return x*x + y*y
EOF
cat <<EOF >lib.py
import mymath
print("Result: {}".format(mymath.f(3,4)))
EOF
touch -t 200711121015 lib.py mymath.py

echo lib.py | python3 -u ./hotload.py lib.py > output &
pid="$!"

sleep 0.1
sed -i.bak 's/f(3,4)/f(4,4)/' lib.py
sleep 0.1
kill "$pid"

strings output | grep -o -m1 'Successfully reloaded lib'
strings output | grep -o -m1 'Result: 25$'
strings output | grep -o -m1 'Result: 32$'

