#!/bin/bash

# Script to run saturated Goodness of Fit test on the combined workspace 

cwd=$(pwd)

maskCRargs="mask_Name1_SR_fail_LOW=0,mask_Name1_SR_fail_SIG=0,mask_Name1_SR_fail_HIGH=0,mask_Name1_SR_pass_LOW=0,mask_Name1_SR_pass_SIG=0,mask_Name1_SR_pass_HIGH=0,mask_Name1_ttbarCR_fail_LOW=1,mask_Name1_ttbarCR_fail_SIG=1,mask_Name1_ttbarCR_fail_HIGH=1,mask_Name1_ttbarCR_pass_LOW=1,mask_Name1_ttbarCR_pass_SIG=1,mask_Name1_ttbarCR_pass_HIGH=1,mask_Name2_S1_muon=0,mask_Name2_S1_electron=0,mask_Name2_S2_muon=0,mask_Name2_S2_electron=0,mask_Name2_S3_muon=0,mask_Name2_S3_electron=0,mask_Name2_S4_muon=0,mask_Name2_S4_electron=0,mask_Name2_V1_muon=0,mask_Name2_V1_electron=0,mask_Name2_V2_muon=0,mask_Name2_V2_electron=0,mask_Name2_V3_muon=0,mask_Name2_V3_electron=0,mask_Name2_V4_muon=0,mask_Name2_V4_electron=0"
setCRparams="var{Name1_ttbarCR.*_mcstats.*}=0,rgx{Name1_ttbarCR.*_mcstats.*}=0,var{Background_ttbarCR.*_bin.*}=0,rgx{Background_ttbarCR.*_bin.*}=0,Background_ttbarCR_rpf_0x0_par0=0,DAK8Top_tag=0",
freezeCRparams="var{ttbarCR.*_mcstats.*},rgx{ttbarCR.*_mcstats.*},var{Background_ttbarCR.*_bin.*},rgx{Background_ttbarCR.*_bin.*},DAK8Top_tag,Background_ttbarCR_rpf_0x0_par0"

sig=$1

if [[ $sig -eq 0 ]]; then
    echo "ERROR: requires signal mass point as argument"
fi

seed=123456
tol=0.5
strat=1
rmin=-1
rmax=3

params=`python scripts/get_parameters_for_impacts.py`

workDir="combination/$sig"
echo "cd ${workDir}"
cd $workDir
w="workspace_masked.root"

echo "Initial fit for impacts"
(set -x; combineTool.py -M Impacts -d $w -m 125 -n "impacts" \
    --doInitialFit --toysFrequentist --rMin $rmin --rMax $rmax \
    --cminDefaultMinimizerStrategy=$strat --cminDefaultMinimizerTolerance "$tol" \
    --X-rtd MINIMIZER_MaxCalls=400000 \
    -v 2)

echo "Running impacts on each parameter"
for p in $params; do
    echo "-----------------------------------------------------------------------------------------------------"
    echo "Running impacts for parameter ${p}..." 
    (set -x; combine -M MultiDimFit -n "_paramFit_impacts_$p" --algo impact \
    --redefineSignalPOIs r -P $p --floatOtherPOIs 1 --saveInactivePOI 1 -d $w \
    --toysFrequentist --cminDefaultMinimizerTolerance $tol \
    --setParameterRanges r=-0.5,20 \
    --cminDefaultMinimizerStrategy=$strat -v 1 --X-rtd MINIMIZER_MaxCalls=400000)
done


cd $cwd
