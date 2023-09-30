#!/bin/bash



echo $0

if [[ $0 == "bash" ]]; then
	echo "Execute me directly."
	exit 1

else
	echo "Ok"
	cd $(dirname $0)/..
	files=$(find . | sort | head -n 10)
	for f in $files; do
		echo "Got file " $f
	done
        TF=$(tempfile)
        echo "Files written to $TF"
        echo "$files" >$TF
	read -p "Check for existence of: (input)" f
	if echo "$files" | grep -q "$f\$"; then
		echo Present
	else
		echo Absent
	fi
fi
