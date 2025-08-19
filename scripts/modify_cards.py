import glob 
from TwoDAlphabet.helpers import execute_cmd
import fileinput

# Modify B2G-23-009 cards to rename nuisances 
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

# Point to new input ROOT files
eosdir = '/eos/home-c/cdifraia/Tprime/nosynch/Unblind/datacards/root_files/'
newdir = 'B2G-23-009/datacards/input/datacards/modified/'

files = glob.glob('B2G-23-009/datacards/input/datacards/*cards_txt/*/*.txt')
for f in files:
    is_tH = True if 'tHq' in f else False
    fname = f.split('/')[-1]
    # This will always overwrite the old modified file, so be careful before running.
    execute_cmd(f'cp {f} {newdir}')
    # replace the "tAq" name with "tHq" for the T->tH files
    if is_tH:
        fname_new = fname.replace('tAq','tHq')
        execute_cmd(f'mv {newdir}{fname} {newdir}{fname_new}')
    # replace the old ROOT file dir with the new (modified) ones 
    execute_cmd(f"sed -i -e 's+{eosdir}+{newdir}+g' {newdir}{fname if not is_tH else fname_new}")
    # replace "shape " with "shapes"
    execute_cmd(f"sed -i -e 's+shape +shapes+g' {newdir}{fname if not is_tH else fname_new}")
    # now replace the systematics 
    for old, new in rename.items():
        execute_cmd(f"sed -i -e 's+{old} +{new}+g' {newdir}{fname if not is_tH else fname_new}")

    # Let's just have combine automatically calculate the rate for B2G-23-009 processes using the TH1::Integral method 
    with open(f'{newdir}{fname if not is_tH else fname_new}','r') as f:
        cardlines = f.readlines()

    for i, line in enumerate(cardlines):
        text = line.split()
        if text[0] != 'rate': 
            continue
        else:
            for val in text:
                if val == 'rate':
                    continue
                else:
                    line = line.replace(val,'-1',1)
            # For some reason for MH100, the first value gets '--1' instead of '-1' so just replace it 
            line = line.replace('--1','-1')
            cardlines[i] = line
            break
    
    with open(f'{newdir}{fname if not is_tH else fname_new}','w') as f:
        f.writelines(cardlines)
