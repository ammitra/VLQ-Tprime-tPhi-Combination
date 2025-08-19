#!/bin/bash
cwd=`pwd`

for MT in {1000..3000..100}; do 
    for MP in {75..250..25}; do 
        if [ $MP -eq 225 ]; then 
            echo "MP=${MP} not used in B2G-23-009, skipping...."
        elif [[ $MT -eq 800 && ($MP -eq 150 || $MP -eq 225) ]]; then 
            echo "${MT}-${MP} not interpolated, skipping...."
        elif [[ $MT -eq 800 && ($MP -eq 150 || $MP -eq 225) ]]; then 
            echo "${MT}-${MP} not interpolated, skipping...."
        elif [[ $MT -eq 900 && $MP -eq 150 ]]; then 
            echo "${MT}-${MP} not interpolated, skipping...."
        elif [[ $MT -eq 1000 && ($MP -eq 150 || $MP -eq 200 || $MP -eq 250) ]]; then 
            echo "${MT}-${MP} not interpolated, skipping...."
        elif [[ $MT -eq 1100 && $MP -eq 250 ]]; then 
            echo "${MT}-${MP} not used in B2G-23-009, skipping...."
        elif [[ $MT -eq 1200 && $MP -eq 250 ]]; then 
            echo "${MT}-${MP} not used in B2G-23-009, skipping...."
        else 
            newDir="combination/${MT}-${MP}"
            if [[ $MP -eq 150 || $MP -eq 225 ]]; then 
                myDir="../Tprime/${MT}-${MP}-INTERPOLATED_unblind_fits"
            else 
                myDir="../Tprime/${MT}-${MP}_unblind_fits"
            fi

            mkdir -p $newDir 
            echo "Creating combined card for signal ${MT}-${MP} in directory ${newDir}/..."
            combineCards.py Name1="${myDir}/card_${MT}-${MP}.txt" Name2="B2G-23-009/datacards/input/datacards/modified/Tprime_tAq_${MT}_MH${MP}_LH_hist.txt" > "${newDir}/${MT}-${MP}.txt"
            # Fix the location for the base.root in my cards
            sed -i -e 's+\./base\.root+base\.root+g' "${newDir}/${MT}-${MP}.txt"
            sed -i -e 's+\.\./Tprime/+\.\./\.\./\.\./Tprime/+g' "${newDir}/${MT}-${MP}.txt"
            # I made a mistake in the script `modify_cards.py`, so just correct it here with sed
            sed -i -e 's+B2G-23-009/datacards/input/datacards/modified/+\.\./\.\./+' "${newDir}/${MT}-${MP}.txt"
            sed -i -e 's+B2G-23-009/datacards/input/datacards/modified+B2G-23-009/datacards/models/modified+' "${newDir}/${MT}-${MP}.txt"

            # B2G-23-009 has additional selection specifically for the tH channel, so let's create a separate directory for these as well. 
            if [[ $MP -eq 125 ]]; then 
                newDir_tH="combination/${MT}-${MP}-tH"
                mkdir -p $newDir_tH
                echo "Creating combined card for signal ${MT}-${MP} (tH channel) in directory ${newDir_tH}/ ..."
                combineCards.py Name1="${myDir}/card_${MT}-${MP}.txt" Name2="B2G-23-009/datacards/input/datacards/modified/Tprime_tHq_${MT}_MH${MP}_LH_hist.txt" > "${newDir_tH}/${MT}-${MP}-tH.txt"
                # Fix the location for the base.root in my cards
                sed -i -e 's+\./base\.root+base\.root+g' "${newDir_tH}/${MT}-${MP}-tH.txt"
                sed -i -e 's+\.\./Tprime/+\.\./\.\./\.\./Tprime/+g' "${newDir_tH}/${MT}-${MP}-tH.txt"
                # I made a mistake in the script `modify_cards.py`, so just correct it here with sed
                sed -i -e 's+B2G-23-009/datacards/input/datacards/modified/+\.\./\.\./+' "${newDir_tH}/${MT}-${MP}-tH.txt"
                sed -i -e 's+B2G-23-009/datacards/input/datacards/modified+B2G-23-009/datacards/models/modified+' "${newDir_tH}/${MT}-${MP}-tH.txt"
            fi
        fi
    done
done