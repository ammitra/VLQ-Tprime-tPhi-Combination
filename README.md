# Combination, B2G-22-001 + B2G-23-009

* B2G-23-009 datacards: https://gitlab.cern.ch/cms-analysis/b2g/b2g-23-009/datacards
* B2G-22-001 datacards: https://gitlab.cern.ch/cms-analysis/b2g/b2g-22-001/datacards

B2G-23-009 naming conventions:
* Stat = uncorrelated
* Syst = correlated
Common uncertainties
* `PF -> Prefire`
* `ParNetSyst -> PNetXbb_tag`
* `lumi_Run2 -> lumi_correlated` (note, this is an lnN nuisance so only needs changed in the card)
* `TT_LHE -> qcd_ren_scale_TT`
* `jer_2016pos -> jer16`
* `jer_2017 -> jer17`
* `jer_2018 -> jer18`
* `pdf_total -> pdf`
* `w_pt -> TptReweight`

# Instructions for combination 

1. Modify the B2G-23-009 workspaces so that common nuisances are named the same following the scheme above. The original workspaces are contained in `B2G-23-009/datacards/models/default/` and the new ones will be located in `B2G-23-009/datacards/models/modified/`.
```
python scripts/modify_workspace.py
```
Importantly, this script will re-scale the B2G-23-009 signal templates (both combined Run2 and separate per-year templates) to match the B2G-22-001 cross sections for the combination. It uses the files `B2G-23-009/datacards/inputs/input_xsec_<year>.json` to obtain the input cross sections used in the semileptonic analysis. It scales the templates by the ratio of the hadronic to semileptonic top decay BRs as well. 

2. Modify the B2G-23-009 cards so that the common nuisances are named the same. Original cards located under `B2G-23-009/datacards/input/datacards/t*_cards_txt/`, the new ones under `B2G-23-009/datacards/input/datacards/modified/`
```
python scripts/modify_cards.py
```

3. Generate the combined cards (only for the mass points in common).
```
source scripts/make_combined_cards.sh
```
* The common mass points are: `MT=[800,3000]` and `MP=75,100,125,150,175,200,250`
* Notably, B2G-23-009 does not include `MP=225` for some reason.
* Some points in B2G-23-009 are not studied b/c the efficincies are too low. These are:
    * `(1100, 250)`
    * `(1200, 250)`
    * `(1000, 200)`
    * `(1000, 250)`

4. Run limits on all the combined points:
* Arbitrary mass point: `./scripts/AsymptoticLimits ${MT}-${MP}`
* B2G-23-009 only (masks B2G-22-001): `./scripts/Limits-B2G-23-009.sh`
* B2G-22-001 only (masks B2G-23-009): `./scripts/Limits-B2G-22-001.sh`
* Run everything (use `screen`): `./scripts/run_combination.sh`

5. Run limits for B2G-23-009 only
```
./scripts/B2G-23-009_specific.sh
```
