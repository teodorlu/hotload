#!/bin/bash
set -e

main(){
    done_chan="${TMPDIR}chan$$"
    mkfifo "$done_chan"
    ( tests "$done_chan" || true ) & pid1=$!
    ( sleep 4 && echo TIMEOUT > "$done_chan" || true ) & pid2=$!
    read msg < "$done_chan"
    nofail silent kill $pid1 $pid2
    case "$msg" in
        TIMEOUT)
            fail "TIMEOUT" ;;
        OK)
            echo "Tests OK!"
            exit ;;
        *)
            fail "Unexpected: $msg" ;;
    esac
}

tests()( done_chan="$1"
    trap 'end' EXIT

    cat <<-EOF >lib.py
	x = 3
	y = 4
	print("Result: {}".format(x*x + y*y))
EOF
    touch -t 200711121015 lib.py

    pipe="${TMPDIR}hotload$$"; mkfifo "$pipe"

    echo lib.py | python -u hotload.py lib.py > "$pipe" & pid=$!

    (
    expect "Running hotload"
    expect "Result: 25"
    expect "Successfully reloaded lib"

    sed -i.bak "s/x = ./x = 4/" lib.py

    expect "Result: 32"
    expect "Successfully reloaded lib"
    ) < "$pipe"

    echo OK > "$done_chan"

    end() {
        [ -z "$pid" ] || nofail silent kill $pid
        [ -e "$pipe" ] && rm "$pipe" || true
    }
)

expect() {
    while IFS= read -r line; do
        case "$line" in
            *$1*)
                echo "Asserted: $1"
                return 0
                ;;
        esac
    done
    echo >&2 "Failed assertion: $1"
    return 1
}

fail() {
    echo >&2 "ERROR: $1"
    exit 1
}

silent() {
    "$@" >/dev/null 2>&1
}

nofail() {
    "$@" || true
}


main "$@"

