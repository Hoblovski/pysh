#!/bin/bash

echo First argument: $1

if [[ $1 == "version" ]]; then
        echo "Example version: 0.1"
        exit 0
else
        time seq 100000000 >/dev/null
        echo "Ok"
        cd $(dirname $0)/..
        files=$(find . | sort | head -n 10)
        for f in $files; do
                echo "Got file " $f
        done
        tf=$(tempfile)
        echo "Files written to $tf"
        echo "$files" >$tf
        read -p "Check for existence of: (input)" f
        if grep "$f$" $tf >/dev/null 2>&1; then
                echo Present
        else
                echo Absent
        fi
fi
