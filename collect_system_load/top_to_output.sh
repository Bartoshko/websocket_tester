#!/bin/bash
echo "execution started.."

while [ true ]; do
    sleep 1
    echo "writing system load to output"
    top -b -n 5 | sed -n '8, 12{s/^ *//;s/ *$//;s/  */./gp;};12q' >> out.txt
done
