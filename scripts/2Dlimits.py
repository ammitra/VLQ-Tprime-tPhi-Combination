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

limits_obs = []

limits = []

files = glob.glob('combination/*/*AsymptoticLimits*.root')

tbqq_BR = 0.991 * 0.673

MTs = np.arange(1000, 3100, 100)
MPs = np.arange(75, 525, 25)

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
                #vals.append(np.nan)
                vals.append(1e-1)
                continue
        elif MP > 250:
            if MP in [275, 300, 325]:
                fname = f'../Tprime/{MT}-{MP}-INTERPOLATED_unblind_fits/higgsCombine_{MT}-{MP}_noCR_workspace.AsymptoticLimits.mH120.root'
            else:
                fname = f'../Tprime/{MT}-{MP}_unblind_fits/higgsCombine_{MT}-{MP}_noCR_workspace.AsymptoticLimits.mH120.root'
            if not os.path.exists(fname):
                #vals.append(np.nan)
                vals.append(1e-1)
                continue
        elif (MT == 1000) and (MP == 150 or MP == 200 or MP == 250):
            #print(f'{MT}-{MP} not interpolated in B2G-22-001, skipping...')
            #vals.append(np.nan)
            vals.append(1e-1)
            continue
        elif (MT == 1100) and (MP == 250):
            #print(f'MPhi = {MP} not used in B2G-23-009, skipping...')
            #vals.append(np.nan)
            vals.append(1e-1)#
            continue
        elif (MT == 1200) and (MP == 250):
            #print(f'MPhi = {MP} not used in B2G-23-009, skipping...')
            #vals.append(np.nan)
            vals.append(1e-1)
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

        # Extra norm factor from B2G-22-001 (input xsec)
        if (MT < 1400):
            norm = 0.1 * 1000.
        else:
            norm = 0.01 * 1000.

        lim = limit * factor * norm

        limits_obs.append([MT, MP, lim])

        vals.append(lim)
    limits.append(vals)

# Use the 2D array
limits = np.array(limits)

fs = 36

def colormesh(xx, yy, lims, label, name, prelim=False):
    fig, ax = plt.subplots(figsize=(14, 12), dpi=150)
    pcol = plt.pcolormesh(xx, yy, lims, norm=matplotlib.colors.LogNorm(vmin=0.1, vmax=1e4), cmap="viridis", linewidth=0, rasterized=True)
    pcol.set_edgecolor('face')
    # plt.title(title)
    plt.xlabel(r"$m_{T^{\prime}}$ [GeV]", fontsize=fs)
    plt.ylabel(r"$m_{\phi}$ [GeV]", fontsize=fs)

    # plt.colorbar(label=label, fontsize=fs)
    cbar = plt.colorbar(label=label)
    cbar.ax.tick_params(labelsize=fs-9)

    hep.cms.label(loc=3 if prelim else 0, ax=ax, label='Preliminary' if prelim else None, rlabel='', data=True, fontsize=fs)
    lumiText = r"138 $fb^{-1}$ (13 TeV)"
    hep.cms.lumitext(lumiText,ax=ax, fontsize=fs)
    plt.savefig(name, bbox_inches="tight")

mxs = np.logspace(np.log10(1000), np.log10(2999), 100, base=10)
mys = np.logspace(np.log10(75), np.log10(500), 100, base=10)

xx, yy = np.meshgrid(mxs, mys)

interpolated = interpolate.LinearNDInterpolator(limits, np.log(limits))

# workaround for \mathcal
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.cal'] = 'stix:italic'

colormesh(xx, yy, interpolated, r'Obs. upper limit on $\sigma\mathcal{B}(t \to bq\overline{q})$ [fb]', 'plots/2Dlimits.pdf', True)