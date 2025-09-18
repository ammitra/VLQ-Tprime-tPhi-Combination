#!/bin/bash

# script to make backups of the limit files

MPs=(75 100 150 175 200 250)

for MP in ${MPs[@]}; do
    for MT in {1000..3000..100}; do
        #./scripts/AsymptoticLimits.sh "${MT}-${MP}"
        mv "combination/${MT}-${MP}/higgsCombine_${MT}-${MP}.AsymptoticLimits.mH120.root" "combination/${MT}-${MP}/higgsCombine_${MT}-${MP}.AsymptoticLimits.mH120.root.backup-before-new-tol-3Sept25"
    done
done
