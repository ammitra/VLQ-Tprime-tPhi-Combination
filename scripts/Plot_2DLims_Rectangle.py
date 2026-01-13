'''
Stolen from Matej:
https://github.com/Boosted-X-H-bb-Y-anomalous-jet/AnomalousSearchPlotting/blob/master/limit_plotting/plotting_limits.py#L97
'''
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
from matplotlib.colors import LogNorm

MTs = np.arange(1000, 3100, 100)
MPs = np.arange(25, 525, 25) # use this one for final plot
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
        elif (MT == 1000) and (MP == 200 or MP == 250):
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

for version in ['Supplementary','Final','Preliminary']:
    # Whether to delineate the regions or not
    for legend in [True, False]:
        # Rectangle plot
        plt.style.use(hep.style.CMS)
        fig, ax = plt.subplots(figsize=(25,15), dpi=200)
        # fontsize
        fs = 36
        # Set and customize axis ticks
        ax.set_yticks(np.arange(25, 525, 25), labels=np.arange(25,525,25), fontsize=fs)
        ax.set_xticks(np.arange(1000, 3100, 100), labels=[f'{v/1000.:.1f}' for v in np.arange(1000,3100,100)], rotation=45, fontsize=fs)
        # Set axis limits with some padding
        ax.set_ylim(0, 525)
        ax.set_xlim(900, 3100)
        # Create color normalization
        norm = LogNorm(vmin=0.1, vmax=20.)
        cmap = plt.cm.viridis

        # First dimension is MTs, second is MPs. We want MTs on X-axis
        for i in range(len(MTs)):
            for j in range(len(MPs)):
                limit_value = limits[i][j]
                print(f'({MTs[i]}, {MPs[j]}) = {limit_value}')
                if not np.isnan(limit_value):
                    # Map limit value to color
                    color = cmap(norm(limit_value))
                    # Create rectangle
                    rect = plt.Rectangle(
                        xy        = (MTs[i]-50, MPs[j]-12.5), 
                        width     = 100, 
                        height    = 25, 
                        facecolor = color, 
                        edgecolor = 'black', 
                        linewidth = 1
                    )
                    ax.add_patch(rect)
                    # Add text annotation
                    if limit_value >= 3.0:
                        color='black'
                    else:
                        color='white'
                    if limit_value >= 100:
                        text = f'{limit_value:.0f}'
                    else:
                        text = f'{limit_value:.1f}'
                    plt.text(MTs[i], MPs[j],
                        text,
                        color=color,
                        ha='center',
                        va='center',
                        fontsize=17,
                        fontweight="bold"
                    )

        # Manually create ScalarMappable
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_clim(vmin=0.1, vmax=20.)

        # Add colorbar
        cbar = plt.colorbar(sm, pad=0.03, ax=ax)
        cbar.set_label('Observed 95% CL upper limits [fb]', fontsize=fs)
        cbar.ax.tick_params(labelsize=fs)
            
        ax.set_xlabel(r'$m_{T^\prime}$ [TeV]', fontsize=fs)
        ax.set_ylabel(r'$m_{\phi}$ [GeV]', fontsize=fs)

        #hep.cms.text("", loc=0, fontsize=fs)
        #lumi = 138
        #lumiText = str(lumi)+ " $fb^{-1}$ (13 TeV)"    
        #hep.cms.lumitext(lumiText, fontsize=fs)

        # Delineate the regions if legend option selected 
        if legend:
            LW = 7 # linewidth
            ORANGE = '#f89c20' # B2G-23-009
            PURPLE = '#7a21dd' # B2G-22-001
            BLUE   = '#5790fc' # Combination
            # First do B2G-23-009
            rect_23009 = plt.Rectangle(
                xy = (MTs[0]-50, MPs[0]-12.5),
                width = 2100,
                height = 48,
                facecolor='none',
                edgecolor=ORANGE,
                linewidth=LW
            )
            ax.add_patch(rect_23009)
            # Now do combination (REGION 1)
            ax.plot([950,3050], [50+14.5,50+14.5], color=BLUE, lw=LW)    # bottom of region 1
            ax.plot([3050,3050], [50+14.5,200+10.5], color=BLUE, lw=LW)  # left of region 1
            ax.plot([1050,3050], [200+10.5,200+10.5], color=BLUE, lw=LW) # top of region 1
            ax.plot([950, 950], [50+14.5, 125+10.5], color=BLUE, lw=LW)      # LEFT
            ax.plot([950, 950], [150+14.5, 175+10.5], color=BLUE, lw=LW)     # LEFT
            ax.plot([1050, 1050], [125+14.5, 150+10.5], color=BLUE, lw=LW)   # LEFT
            ax.plot([1050, 1050], [175+14.5, 200+10.5], color=BLUE, lw=LW)   # LEFT
            ax.plot([950, 1050], [125+14.5, 125+14.5], color=BLUE, lw=LW)
            ax.plot([950, 1050], [150+10.5, 150+10.5], color=BLUE, lw=LW)
            ax.plot([950, 1050], [175+14.5, 175+14.5], color=BLUE, lw=LW)
            # Now do combination (REGION 2)
            rect_comb2 = plt.Rectangle((MTs[3]-50,MPs[9]-10.5), width=1800, height=21, facecolor='none', edgecolor=BLUE, linewidth=LW)
            ax.add_patch(rect_comb2)
            # Now do B2G-22-001
            rect_22001_1 = plt.Rectangle((MTs[1]-50,MPs[8]-10.5), width=2000, height=21, facecolor='none', edgecolor=PURPLE, linewidth=LW)
            ax.add_patch(rect_22001_1)
            # 22-001 (REGION 2)
            ax.plot([1650,3050], [250+14.5,250+14.5], color=PURPLE, lw=LW) # bottom
            ax.plot([3050,3050], [250+14.5,350+14.5], color=PURPLE, lw=LW) # right
            ax.plot([950,3050], [350+14.5,350+14.5], color=PURPLE, lw=LW) # top
            ax.plot([1650,1650], [250+14.5,325+10.5], color=PURPLE, lw=LW) # left
            ax.plot([950,950], [325+14.5,350+14.5], color=PURPLE, lw=LW) # left
            ax.plot([950,1650], [325+10.5,325+10.5], color=PURPLE, lw=LW) # bottom2 
            # 22-001 (REGION 3 + 4)
            rect_22001_3 = plt.Rectangle((MTs[0]-54.5,MPs[-3]-12.5), width=2105, height=25, facecolor='none', edgecolor=PURPLE, linewidth=LW)
            rect_22001_4 = plt.Rectangle((MTs[0]-54.5,MPs[-1]-12.5), width=2105, height=25, facecolor='none', edgecolor=PURPLE, linewidth=LW)
            ax.add_patch(rect_22001_3)
            ax.add_patch(rect_22001_4)

            # Now make legend 
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(edgecolor=PURPLE, facecolor='none', label=r'$\phi\to b\overline{b},\,t\to bq\overline{q}^\prime$', linewidth=LW),
                Patch(edgecolor=ORANGE, facecolor='none', label=r'$\phi\to b\overline{b},\,t\to b\ell\nu$', linewidth=LW),
                Patch(edgecolor=BLUE, facecolor='none', label=r'Combination', linewidth=LW)
            ]
            ax.legend(loc=(0.08,0.72), handles=legend_elements, ncol=3, fontsize=fs)


        label = version if version != 'Final' else ''
        hep.cms.text(label, loc=0, fontsize=fs)
        lumi = 138
        lumiText = str(lumi)+ " $fb^{-1}$ (13 TeV)"
        hep.cms.lumitext(lumiText, fontsize=fs)

        # Save out
        plt.tight_layout()
        fig.savefig(f'plots/Limits_2D_rectangle_obs_{"withLegend" if legend else "noLegend"}_{version}.pdf', bbox_inches='tight')
