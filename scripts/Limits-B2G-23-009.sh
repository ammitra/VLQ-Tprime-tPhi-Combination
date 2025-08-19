#!/bin/bash
maskCRargs="mask_Name1_SR_fail_LOW=1,mask_Name1_SR_fail_SIG=1,mask_Name1_SR_fail_HIGH=1,mask_Name1_SR_pass_LOW=1,mask_Name1_SR_pass_SIG=1,mask_Name1_SR_pass_HIGH=1,mask_Name1_ttbarCR_fail_LOW=1,mask_Name1_ttbarCR_fail_SIG=1,mask_Name1_ttbarCR_fail_HIGH=1,mask_Name1_ttbarCR_pass_LOW=1,mask_Name1_ttbarCR_pass_SIG=1,mask_Name1_ttbarCR_pass_HIGH=1",
setCRparams="var{Name1_ttbarCR.*_mcstats.*}=0,rgx{Name1_ttbarCR.*_mcstats.*}=0,var{Background_ttbarCR.*_bin.*}=0,rgx{Background_ttbarCR.*_bin.*}=0,Background_ttbarCR_rpf_0x0_par0=0,DAK8Top_tag=0,var{Name1_SR.*_mcstats.*}=0,rgx{Name1_SR.*_mcstats.*}=0,var{Background_SR.*_bin.*}=0,rgx{Background_SR.*_bin.*}=0"
freezeCRparams="var{ttbarCR.*_mcstats.*},rgx{ttbarCR.*_mcstats.*},var{Background_ttbarCR.*_bin.*},rgx{Background_ttbarCR.*_bin.*},DAK8Top_tag,Background_ttbarCR_rpf_0x0_par0,var{SR.*_mcstats.*},rgx{SR.*_mcstats.*},var{Background_SR.*_bin.*},rgx{Background_SR.*_bin.*}"

sig=$1

if [[ $sig -eq 0 ]]; then 
    echo "ERROR: requires signal mass point as argument"
    exit 0
fi

seed=123456
tol=10
strat=0
rmax=3

cwd=`pwd`
newDir="combination/$sig"
echo "cd ${newDir}"
cd $newDir

if [[ ! -f "workspace_masked.root" ]]; then 
    echo "Creating workspace with channel masks from the txt file..."
    text2workspace.py "${sig}.txt" --channel-masks -o workspace_masked.root
else 
    echo "workspace_masked.root already exists..."
fi

(set -x; combine -M AsymptoticLimits -d workspace_masked.root --saveWorkspace -v 2 -n "_B2G-23-009" -s $seed --setParameters "${maskCRargs},${setCRparams}" --freezeParameters "${freezeCRparams}" --cminDefaultMinimizerTolerance $tol --cminDefaultMinimizerStrategy $strat --X-rtd MINIMIZER_MaxCalls=400000 --rMin -1 --rMax $rmax)

cd $cwd
