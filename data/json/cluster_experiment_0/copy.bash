#!/bin/bash
for i in $(seq 0 ${2:-24})
do
	cp town/$1 town_$i/$1
done
