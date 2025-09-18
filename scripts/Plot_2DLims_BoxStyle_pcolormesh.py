import os, glob
import numpy as np
from scipy import interpolate
import matplotlib
import matplotlib.pyplot as plt
import mplhep as hep
import matplotlib.ticker as mticker
import ROOT
import subprocess
import pandas as pd
import argparse
import glob
import seaborn as sns
import json

MTs = np.arange(1000, 3100, 100)
MPs = np.arange(25, 525, 25)
#MPs = np.arange(75, 275, 25)
#MPs = np.arange(75, 525, 25)
#MPs = np.array([i for i in MPs if i != 375 and i != 400 and i != 425 and i != 475])

def mxmy(sample):
    # Example input: combination/1900-100/higgsCombine_1900-100.AsymptoticLimits.mH120.root
    mX = float(sample.split('/')[1].split('-')[0])
    mY = float(sample.split('/')[1].split('-')[1])
    return (mX, mY)

limits_obs = []

limits = []

files = glob.glob('combination/*/*AsymptoticLimits*.root')

tbqq_BR = 0.991 * 0.673

for MT in MTs:
    vals = []
    for MP in MPs:
        # Check for mass points that aren't used 
        if MP == 225:
            #print(f'MPhi = {MP} not used in B2G-23-009, skipping...')
            #vals.append(np.nan)
            #continue
            fname = f'../Tprime/{MT}-{MP}-INTERPOLATED_unblind_fits/higgsCombine_{MT}-{MP}_noCR_workspace.AsymptoticLimits.mH120.root'
            if not os.path.exists(fname):
                vals.append(np.nan)
                continue
        elif MP > 250:
            if MP in [275, 300, 325]:
                fname = f'../Tprime/{MT}-{MP}-INTERPOLATED_unblind_fits/higgsCombine_{MT}-{MP}_noCR_workspace.AsymptoticLimits.mH120.root'
            else:
                fname = f'../Tprime/{MT}-{MP}_unblind_fits/higgsCombine_{MT}-{MP}_noCR_workspace.AsymptoticLimits.mH120.root'
            if not os.path.exists(fname):
                vals.append(np.nan)
                continue
        elif (MT == 1000) and (MP == 150 or MP == 200 or MP == 250):
            #print(f'{MT}-{MP} not interpolated in B2G-22-001, skipping...')
            vals.append(np.nan)
            continue
        elif (MT == 1100) and (MP == 250):
            #print(f'MPhi = {MP} not used in B2G-23-009, skipping...')
            vals.append(np.nan)
            continue
        elif (MT == 1200) and (MP == 250):
            #print(f'MPhi = {MP} not used in B2G-23-009, skipping...')
            vals.append(np.nan)
            continue
        else:
            pass 
        # Get the observed limits 
        if MP != 225 and MP <= 250:
            if MP == 125:
                f = ROOT.TFile.Open(f'combination/{MT}-{MP}-tH/higgsCombine_{MT}-{MP}-tH.AsymptoticLimits.mH120.root','READ')
            else:    
                f = ROOT.TFile.Open(f'combination/{MT}-{MP}/higgsCombine_{MT}-{MP}.AsymptoticLimits.mH120.root','READ')
        else:
            f = ROOT.TFile.Open(fname)
        limTree = f.Get('limit')
        limTree.GetEntry(5) # obs
        factor = 1./tbqq_BR
        factor = 1.0
        limit = limTree.limit

        # norm factor from B2G-23-009 (input xsec)
        if MP == 25 or MP == 50:
            # Get the B2G-23-009 input cross sections. APV corresponds to postVFP
            input_16    = json.load(open('B2G-23-009/datacards/input/Cross_sections_2016preVFP_fb.json'))
            input_16APV = json.load(open('B2G-23-009/datacards/input/Cross_sections_2016postVFP_fb.json'))
            input_17    = json.load(open('B2G-23-009/datacards/input/Cross_sections_2017_fb.json'))
            input_18    = json.load(open('B2G-23-009/datacards/input/Cross_sections_2018_fb.json'))
            xsec16    = input_16[f'Tprime_tAq_{MT}_MH{MP}_LH_2016preVFP']
            xsec16APV = input_16APV[f'Tprime_tAq_{MT}_MH{MP}_LH_2016postVFP']
            xsec17    = input_17[f'Tprime_tAq_{MT}_MH{MP}_LH_2017']
            xsec18    = input_18[f'Tprime_tAq_{MT}_MH{MP}_LH_2018']
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
            norm = old_xsec # fb
        else:
            # Extra norm factor from B2G-22-001 (input xsec)
            if (MT < 1400):
                norm = 0.1 * 1000.
            else:
                norm = 0.01 * 1000.

        lim = limit * factor * norm

        limits_obs.append([MT, MP, lim])

        vals.append(lim)
    limits.append(vals)

# Make a dataframe just in case
for i, arr in enumerate(limits_obs):
    limits_obs[i] = np.array(arr)
df = pd.DataFrame(limits_obs, columns=['MT','MP','Limit (fb)'])

# Use the 2D array
limits = np.array(limits)


# print(limits[:,-2])
# limits = np.delete(limits, obj=-2, axis=1)

fs = 36 # fontsize
plt.style.use(hep.style.CMS)
hep.style.use("CMS")
figsize=(35,25)
fig, ax = plt.subplots(figsize=figsize, dpi=150)
formatter = mticker.ScalarFormatter(useMathText=True)
formatter.set_powerlimits((-3, 3))
plt.rcParams.update({"font.size": fs})
ax.minorticks_off()


# MPs = np.delete(MPs, obj=-2, axis=0)
Y,X=np.meshgrid(MPs, MTs)
mappable = ax.pcolormesh(
    X,#MTs,
    Y,#MPs, 
    limits,
    cmap='viridis', 
    norm=matplotlib.colors.LogNorm(vmin=np.nanmin(limits)+1e-1, vmax=np.nanmax(limits)),
    shading='auto'
)

mappable.set_edgecolor('face')
cbar = plt.colorbar(mappable, pad=0.01, label=r'Obs. upper limit on $\sigma(pp \to T^\prime bq)\mathcal{B}(T^\prime \to t\phi)$ [fb]')
cbar.ax.tick_params(labelsize=fs) 


# Set axis labels
ax.set_xlabel(r"$m_{T^\prime}$ [GeV]",fontsize=fs)
ax.set_ylabel(r"$m_\phi$ [GeV]",fontsize=fs)

hep.cms.label(loc=0, ax=ax, label='WiP', rlabel='', data=True, fontsize=fs)
lumiText = r"138 $fb^{-1}$ (13 TeV)"
hep.cms.lumitext(lumiText,ax=ax, fontsize=fs)

ax.set_xticks(MTs)
ax.set_xticklabels(MTs, fontsize=fs, rotation=90)

ax.set_yticks(MPs)
ax.set_yticklabels(MPs, fontsize=fs)

for i in range(limits.shape[0]):
    for j in range(limits.shape[1]):
        x_center = MTs[i]
        y_center = MPs[j]
        if np.isnan(limits[i, j]):
            continue
        else:
            ax.text(x_center, y_center, f'{limits[i, j]:.1f}',
                ha='center', va='center', color='black', fontsize=fs-6, rotation=45)



fig.savefig('plots/limits_2D_box_pcolormesh.pdf',bbox_inches='tight')
