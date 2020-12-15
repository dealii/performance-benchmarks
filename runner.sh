#!/bin/bash

# this file is executed by Jenkins, usage:
#   runner.sh <cmd> <output-file> <sha1>
#
# cmd is one of:
#   update - grab new revisions from upstream and test them
#   reinit - delete database and rerun old files
#   single - test a given revision and do not record it
#
# output-file: a html file to write

cmd=$1
output=$2
sha=$3

echo "cmd=<${cmd}> output=<${output}>"

if [ "${cmd}" = "reinit" ]; then
    echo "creating new db:"
    python3 render.py newdb
    python3 runner.py newdb
    echo "running old:"
    ./old.sh
    echo "rendering"
    python3 render.py render >$output

elif [ "${cmd}" = "update" ]; then
    python3 runner.py run-all
    python3 render.py render >$output
elif [ "${cmd}" = "single" ]; then
    cp render.db render.db.backup
    cd dealii;git fetch origin $sha:temp;git checkout temp;cd ..
    ./test.sh
    python3 render.py render >$output
    cp render.db.backup render.db # overwrite to not keep results
elif [ "${cmd}" = "old" ]; then
    ./old.sh
    echo "rendering"
    python3 render.py render >$output

else
    echo "error: invalid command ${cmd} " | tee $output
    exit 1
fi
echo "done"
