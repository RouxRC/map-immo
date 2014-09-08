#!/bin/bash

./list-agences.py > agences.csv

grep -P "\t(Code Postal|75\d\d\d)\t" agences.tsv |
  awk -F "\t" '{print "\""$1"\",\""$2"\",\""$3"\","$4","$5","$6}' > agences-paris.csv

