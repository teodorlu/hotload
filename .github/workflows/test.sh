#!/usr/bin/env bash
set -e
trap 'end EXIT' EXIT
trap 'end TERM' TERM
trap 'end INT' INT
PID=$$

main(){
    done_chan="${TMPDIR}chan$$"
    mkfifo "$done_chan"
    ( tests "$done_chan" || true ) & pid1=$!
    ( sleep 4 && echo TIMEOUT > "$done_chan" || true ) & pid2=$!
    read msg < "$done_chan"
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

tests(){ done_chan="$1"
    trap '[ -z "$pid" ] || kill $pid; [ -e "$pipe" ] && rm "$pipe" || true' EXIT

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
}

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

end() {
    case "$1" in
        EXIT)
            trap "exit $?" TERM ;;
        TERM)
            trap - TERM ;;
        INT)
            trap - INT
            trap 'trap - TERM; kill -s INT $$' TERM ;;
    esac
    trap - EXIT
    if [ -e "$done_chan" ]; then rm "$done_chan"; fi
    silent kill $(descendants)
}

descendants() {
    ps -o pid -o ppid | piddescendants $PID
}
piddescendants() {
    # Prints given PID preceded by all its (great...)-grandchildren and children
    awk -v root=$1 'NR > 1 {
        parent[$1] = $2
    } END {
        for (p in parent) {
            d = 0
            c = p
            while (c in parent) {
                if (c == root)
                    depth[d] = (depth[d] " " p)
                else
                    d++
                c = parent[c]
            }
        }
        count = 0
        for (i in depth) count++
        for (d = count - 1; d >= 0; d--) {
            print depth[d]
        }
    }'
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

