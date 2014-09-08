#!/bin/bash

./list-agences.py > agences.csv

echo '"nom","description",lat,lon' > agences-paris.csv
grep -P "\t(75\d\d\d)\t" agences.tsv |
  awk -F "\t" '{print "\""$1"\",\""$2" "$4"\n"$3"\","$5","$6}' >> agences-paris.csv

