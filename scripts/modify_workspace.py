import glob
import ROOT
import json

# Modify B2G-23-009 workspaces to rename nuisances 
rename = {
    'PF': 'Prefire',
    'ParNetSyst': 'PNetXbb_tag',
    'TT_LHE': 'qcd_ren_scale_TT',
    'jer_2016pos': 'jer16',
    'jer_2017': 'jer17',
    'jer_2018': 'jer18',
    'jes_2016pos': 'jes16',
    'jes_2017': 'jes17',
    'jes_2018': 'jes18',
    'pdf_total': 'pdf',
    'w_pt': 'TptReweight'
}

mps = [25, 50, 75, 100, 125, 150, 175, 200, 250, 350, 450, 500]
# Get the B2G-23-009 input cross sections. APV corresponds to postVFP
input_16    = json.load(open('B2G-23-009/datacards/input/Cross_sections_2016preVFP_fb.json'))
input_16APV = json.load(open('B2G-23-009/datacards/input/Cross_sections_2016postVFP_fb.json'))
input_17    = json.load(open('B2G-23-009/datacards/input/Cross_sections_2017_fb.json'))
input_18    = json.load(open('B2G-23-009/datacards/input/Cross_sections_2018_fb.json'))

def scale(hName, hist):
    # TEST -----------------------------------------------------------
    # Rescale the histograms so that they match the input normalization in B2G-22-001. 
    # B2G-22-001 uses normalization:
    #   if (MT < 1400):
    #       norm = 0.1 * 1000.   = 100 fb
    #   else:
    #       norm = 0.01 * 1000.  = 10 fb
    mt = hName.split('_')[2]
    mp = hName.split('_')[3].replace('MH','')
    # Get year 
    if '2016pre' in hName:
        key = f'Tprime_tAq_{mt}_MH{mp}_LH_2016preVFP'
        d = input_16
    elif '2016pos' in hName:
        key = f'Tprime_tAq_{mt}_MH{mp}_LH_2016postVFP'
        d = input_16APV
    elif '2017' in hName:
        key = f'Tprime_tAq_{mt}_MH{mp}_LH_2017'
        d = input_17
    elif '2018' in hName:
        key = f'Tprime_tAq_{mt}_MH{mp}_LH_2018'
        d = input_18
    else:
        # Run 2, calculate cross section from the luminosity-weighted average
        key = None

    # Get the cross section
    #old_xsec = theory_xsec_23009[mt][mps.index(int(mp))]
    if key:
        old_xsec = d[key]
    else:
        xsec16    = input_16[f'Tprime_tAq_{mt}_MH{mp}_LH_2016preVFP']
        xsec16APV = input_16APV[f'Tprime_tAq_{mt}_MH{mp}_LH_2016postVFP']
        xsec17    = input_17[f'Tprime_tAq_{mt}_MH{mp}_LH_2017']
        xsec18    = input_18[f'Tprime_tAq_{mt}_MH{mp}_LH_2018']
        # Luminosities: 
        L16    = 16800.0
        L16APV = 19500.0
        L17    = 41521.427777
        L18    = 59692.687741
        LTotal = L16 + L16APV + L17 + L18
        # Lumi fractions:
        F16    = L16 / LTotal
        F16APV = L16APV / LTotal
        F17    = L17 / LTotal
        F18    = L18 / LTotal
        # Xsec, weighted average
        old_xsec = (xsec16 * F16) + (xsec16APV * F16APV) + (xsec17 * F17) + (xsec18 * F18)

    if int(mt) < 1400:
        my_xsec = 100
    else:
        my_xsec = 10
    sf = my_xsec / old_xsec
    # Now factor in the fact that BR(t->blv) is rouhgly half that of BR(t->bqq) (0.33 vs 0.67)
    sf *= (0.33/0.67)
    hist.Scale(sf)

files = glob.glob('B2G-23-009/datacards/models/default/*.root')
for fName in files:
    f = ROOT.TFile.Open(fName,'READ')
    fOut = ROOT.TFile.Open(fName.replace('default','modified'),'RECREATE')
    fOut.cd()
    dirs = [d.GetName() for d in f.GetListOfKeys()]
    for d in dirs:
        print(f'Modifying histos in {fName}:{d}')
        fOut.mkdir(d)
        fOut.cd(d)
        dir = f.Get(d)
        hists = [h.GetName() for h in dir.GetListOfKeys()]
        total = 0
        for i, h in enumerate(hists):
            print(f'Running on hist {i}/{len(hists)}...',end='\r',flush=True)
            hist = dir.Get(h)
            hName = hist.GetName()
            found = False
            for oldName in rename.keys():
                if oldName in hName:
                    newHist = hist.Clone(hName.replace(oldName,rename[oldName]))

                    # TEST 
                    if 'Tprime' in hName:
                        scale(hName, newHist)

                    newHist.Write()
                    found = True
                    total += 1
                    break
                else:
                    continue
            if not found:
                newHist = hist.Clone(hName)

                # TEST 
                if 'Tprime' in hName:
                    scale(hName, newHist)

                newHist.Write()


        print(f'Renamed {total}/{len(hists)} histograms...')
    fOut.Close()