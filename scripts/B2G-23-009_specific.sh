#!/bin/bash

sig=$1

if [[ $sig -eq 0 ]]; then
    echo "ERROR: requires signal mass point as argument"
    exit 0
fi

seed=123456
tol=0.5
strat=1
rmax=100

cwd=`pwd`
newDir="combination/$sig"
echo "cd ${newDir}"
mkdir -p $newDir
cd $newDir

MT="$(cut -d'-' -f1 <<<"$sig")"
MP="$(cut -d'-' -f2 <<<"$sig")"

# Copy the default Combine card
if [[ ! -f "card.txt" ]]; then 
    echo "Copying Combine card to local dir..."
    cp "../../B2G-23-009/datacards/input/datacards/tPhi_cards_txt/Tprime_tAq_${MT}_MH${MP}_LH/Tprime_tAq_${MT}_MH${MP}_LH_hist.txt" "./${sig}.txt"
else 
    echo "Already have a Combine card for $sig..."
fi

# Modify the card to point to the original RooWorkspace
sed -i -e 's+/eos/home-c/cdifraia/Tprime/nosynch/Unblind/datacards/root_files/+../../B2G-23-009/datacards/models/default/+g' "${sig}.txt"

# Create a masked workspace
if [[ ! -f "workspace_masked.root" ]]; then
    echo "Creating workspace with channel masks from the txt file..."
    text2workspace.py "${sig}.txt" --channel-masks -o workspace_masked.root
else
    echo "workspace_masked.root already exists..."
fi

if [[ ! -f "higgsCombine_${sig}.AsymptoticLimits.mH120.root" ]]; then 
    echo "Running ML fit for ${sig}..."
    (set -x; combine -M AsymptoticLimits -d workspace_masked.root --saveWorkspace -v 2 -n "_${sig}" -s $seed --cminDefaultMinimizerTolerance $tol --cminDefaultMinimizerStrategy $strat --X-rtd MINIMIZER_MaxCalls=400000 --rMin -1 --rMax $rmax)
else
    echo "Already run ML fit for ${sig}..."
fi


cd $cwd
