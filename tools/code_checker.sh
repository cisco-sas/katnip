#!/bin/sh

_checkcommand() {
    hash $1 2>/dev/null
}

#
# Check for some possible issues
#
echo "Looking for potential issues in the code"

base_dir=$(cd $(dirname $0)/..; pwd)

#
# We should use logger in our code
#
echo "=== Using print instead of logger ==="
find $base_dir -name "*.py" -exec grep -Hn -e "^\s*print" {} \;

#
# Run pyflakes
#
if _checkcommand pyflakes; then
    echo "=== running pep8 compliance test ==="
    pyflakes $base_dir/katnip/
fi