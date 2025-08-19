#!/bin/bash

MPs=(75 100 150 175 200 250)

for MP in ${MPs[@]}; do 
    for MT in {1000..3000..100}; do 
        ./scripts/AsymptoticLimits.sh "${MT}-${MP}"
    done
done