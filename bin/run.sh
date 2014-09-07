#!/bin/bash

cd $(dirname $0)/..

mkdir -p data
if ! test -f data/bano-75.csv; then
  curl -sL "https://github.com/osm-fr/bano-data/blob/master/bano-75.csv" > data/bano-75.csv
fi

./list-agences.py > data/agences.csv

./localize-agences.py > data/adresses.csv

