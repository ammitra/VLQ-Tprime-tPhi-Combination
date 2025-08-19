import os, glob
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mplhep as hep
import matplotlib.ticker as mticker
import ROOT
import subprocess
import pandas as pd
from collections import OrderedDict
import argparse

MTs = range(1000,3100,100)

# 0-4 are m2,m1,exp,p1,p2 sigma limits, 5 is observed
limits = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

tbqq_BR = 0.991 * 0.6732 # Wqq taken from https://arxiv.org/pdf/2201.07861
tblv_BR = 0.991 * 0.324
hbb_BR = 5.84E-1 # Hbb taken from table 11.3: https://pdg.lbl.gov/2016/

for MT in MTs:
    f = ROOT.TFile.Open(f'combination/{MT}-125-tH/higgsCombine_{MT}-125-tH.AsymptoticLimits.mH120.root', 'READ')
    #f = ROOT.TFile.Open(f'../Tprime/{MT}-125_unblind_fits/higgsCombine_{MT}-125_noCR_workspace.AsymptoticLimits.mH120.root', 'READ')
    limTree = f.Get('limit')
    if not limTree:
        print(f'ERROR: signal {MT}-125 has no limit TTree...')
        continue 
    for i in range(6):
        if not limTree.GetEntry(i):
            print(f'ERROR: signal {MT}-125 missing limit entry {i}')
        limTree.GetEntry(i)
        factor = 1./(hbb_BR * tbqq_BR )
        limit = limTree.limit

        # Extra norm factor from B2G-22-001 (input xsec)
        if (MT < 1400):
            norm = 0.1 * 1000.
        else:
            norm = 0.01 * 1000.

        # Fix the mistakes in xsec from B2G-23-009
        # if MT == 2200:
        #     fix = 0.05855 / 0.00855
        # elif MT == 2600:
        #     fix = 0.02646 / 0.00646
        # elif MT == 2700:
        #     fix = 0.02196 / 0.00196
        # elif MT == 2800:
        #     fix = 0.018170000000000002 / 0.00817
        # elif MT == 2900: 
        #     fix = 0.014929999999999999 / 0.00493
        # elif MT == 3000:
        #     fix = 0.01225 / 0.00225
        # else:
        #     fix = 1.0
        fix = 1.0

        lim = limit * factor * norm * fix

        limits[i].append(lim)

        if MT == 2600:
            print(f'limit 2600: {lim}')



plt.style.use([hep.style.CMS])
fig, ax = plt.subplots(figsize=(14,10), dpi=200)

# Fontsize
fs = 36

# workaround for \mathcal
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.cal'] = 'stix:italic'

green = '#607641' 
yellow = '#F5BB54'

ax.set_xlim([800, 3000])    # the x-axis is plotting mT 
ax.set_yscale('log')

m2 = limits[0]
m1 = limits[1]
med = limits[2]
p1 = limits[3]
p2 = limits[4]
obs = limits[5]

ax.fill_between(MTs, m2, p2, color=yellow, label='95% CL')
ax.fill_between(MTs, m1, p1, color=green, label='68% CL')
ax.plot(MTs, med, color='black', linewidth=2.5, linestyle='--', label='Expected')
ax.plot(MTs, obs, color='black', linewidth=2.5, linestyle='-', marker='o', label='Observed')

ax.set_ylabel(
    r'$\sigma(pp \to T^\prime bq)$ $\mathcal{B}(T^\prime \to tH)$ [fb]',
    fontsize=fs
)

'''
theoryDF = pd.read_csv('../Tprime/limits/theory/TopPartners_SingleProduction/interpreted_tables/sigma_T_Tbj.csv')
# Get the subset of the columns for the sigma and uncertainty for the singlet 1% and 5% widths 
subset = theoryDF[['mass','sigma(Tbj)(pb)_G/MQ=1%(singlet)','sigma(Tbj)(pb)_G/MQ=1%(singlet)_Down','sigma(Tbj)(pb)_G/MQ=1%(singlet)_Up','sigma(Tbj)(pb)_G/MQ=5%(singlet)','sigma(Tbj)(pb)_G/MQ=5%(singlet)_Down','sigma(Tbj)(pb)_G/MQ=5%(singlet)_Up']]
# Limit to only 800 GeV+
subset = subset[subset['mass']>=1000]
# Now get the arrays. Remember that all values are in pb, so we need to scale 
mTheory = subset['mass'].to_numpy()
XS1_nom = subset['sigma(Tbj)(pb)_G/MQ=1%(singlet)'].to_numpy()
XS1_up  = subset['sigma(Tbj)(pb)_G/MQ=1%(singlet)_Up'].to_numpy()
XS1_dn  = subset['sigma(Tbj)(pb)_G/MQ=1%(singlet)_Down'].to_numpy()
XS5_nom = subset['sigma(Tbj)(pb)_G/MQ=5%(singlet)'].to_numpy()
XS5_up  = subset['sigma(Tbj)(pb)_G/MQ=5%(singlet)_Up'].to_numpy()
XS5_dn  = subset['sigma(Tbj)(pb)_G/MQ=5%(singlet)_Down'].to_numpy()

for arr in [XS1_nom, XS1_up, XS1_dn, XS5_nom, XS5_up, XS5_dn]:
    for i in range(len(arr)):
        arr[i] = arr[i] * 1000. * 0.25 # factor of 0.25 

# Plot the nominal theory xsecs for 1% and 5% width
ax.plot(mTheory, XS1_nom, linewidth=2.5, label=r'$\sigma(NLO),$ Singlet $T^{\prime},$ $\Gamma/m_{T^{\prime}}=$1%', color='#e42536')
ax.plot(mTheory, XS5_nom, linewidth=2.5, label=r'$\sigma(NLO),$ Singlet $T^{\prime},$ $\Gamma/m_{T^{\prime}}=$5%', color='#5790fc')
# Now plot the uncertainty as a hatched region
ax.fill_between(mTheory, XS1_dn, XS1_up, color='#e42536', alpha=0.5, linewidth=0)
ax.fill_between(mTheory, XS5_dn, XS5_up, color='#5790fc', alpha=0.5, linewidth=0)
'''

# Theory cross sections directly from Francesco
x1 = np.array([1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600])
x5 = np.array([1000,1100,1200,1300,1400,1500,1600,1700,1800,2000,2200,2400,2600])

y1 = np.array([
    14.550,
    8.640,
    5.342,
    3.390,
    2.197,
    1.448,
    0.9743,
    0.6638,
    0.4588,
    0.3201,
    0.2256,
    0.119,
    0.0671,
    0.0401
])
y5 = np.array([
    69.8805,
    42.0605,
    26.1005,
    16.6795,
    10.8675,
    7.239,
    4.894,
    3.366,
    2.3395,
    1.172,
    0.631556,
    0.36267,
    0.221838
])

# Plot the nominal theory xsecs for 1% and 5% width
ax.plot(x1, y1, linewidth=2.5, label=r'$\sigma(NLO),$ Singlet $T^{\prime},$ $\Gamma/m_{T^{\prime}}=$1%', color='#e42536')
ax.plot(x5, y5, linewidth=2.5, label=r'$\sigma(NLO),$ Singlet $T^{\prime},$ $\Gamma/m_{T^{\prime}}=$5%', color='#5790fc')

# Re-plot the median expected and observed limits so they're above theory
ax.plot(MTs, med, color='black', linewidth=2.5, linestyle='--')
ax.plot(MTs, obs, color='black', linewidth=2.5, linestyle='-')

# Individual results (B2G-22-001 and B2G-23-009) OBSERVED
B2G_22_001 = np.array([25.16437256945517,30.85610480179935,30.941524694487136,26.607378475308707,22.037054927433825,16.87977483390729,13.95966283338852,15.565000624894477,11.242948802944115,9.959881335062384,10.235842064325476,9.329921430118166,8.704610043857048,8.109859824286733,8.046151076177573,7.86581949928322,7.874056174686013,7.857108786020054,8.055990200360498,8.180352315994078,8.172408868730468])
B2G_23_009 = np.array([111.59235984,  51.82023719,  29.1393809 ,  21.09403163,
        16.39941335,  10.87235659,   6.02779165,   4.04159538,
         3.01059824,   2.60975119,   2.27420451,   2.00587907,
         1.82171748,   1.63388171,   1.53273111,   1.4614648 ,
         1.36781367,   1.30498072,   1.2110743 ,   1.11966976,
         1.0456139 ])
# EXPECTED
B2G_22_001_exp = np.array([48.124991206601614,38.499994495133556,28.874993959034832,24.062495603300807,17.324997140347033,15.399997798053423,13.474996925907543,13.474996925907543,9.624998241320322,9.624998241320322,9.624998241320322,8.647459357436228,6.737498462953772,5.774998791806967,5.774998791806967,5.774998791806967,5.774998791806967,5.774998791806967,5.774998791806967,5.774998791806967,5.774998791806967])
B2G_23_009_exp = np.array([128.5842955112457, 48.7729981541633, 26.70712582767, 18.9873520284891, 15.920100733637799, 13.5450521484017, 9.067426435649299, 6.431879941374, 4.876160994172, 4.3437932617962, 3.9556259289383005, 3.3271613065153, 2.8224063571542, 2.3681479506194, 2.1122661419211997, 1.9437948940321002, 1.7868216382339, 1.6383039765059, 1.4881269307807, 1.3377306750043998, 1.2250895379111])


ax.plot(MTs, B2G_22_001, color='#832db6', linewidth=2.5, linestyle='solid', label='B2G-22-001')
ax.plot(MTs, B2G_23_009, color='#e76300', linewidth=2.5, linestyle='solid', label='B2G-23-009')

ax.plot(MTs, B2G_22_001_exp, color='#832db6', linewidth=2.5, linestyle='dashed')
ax.plot(MTs, B2G_23_009_exp, color='#e76300', linewidth=2.5, linestyle='dashed')


# Legend stuff 
theory_handles = []
theory_labels  = []
limit_handles  = []
limit_labels   = []
handles, labels = ax.get_legend_handles_labels()
for handle, label in zip(handles, labels):
    if 'NLO' in label:
        theory_handles.append(handle)
        theory_labels.append(label)
    else:
        limit_handles.append(handle)
        limit_labels.append(label)

# Specify that this is mphi = mh
ax.text(0.24, 0.95, r'$m_{\phi} = m_{H} = 125$ GeV', ha='center', va='top', fontsize=fs-5, transform=ax.transAxes, fontproperties='Tex Gyre Heros')

# Now place the legends
# Add first legend for signal in upper right
first_legend = ax.legend(
    theory_handles, 
    theory_labels, 
    ncol=1, 
    loc="upper left",
    fontsize=fs-12,
    bbox_to_anchor=(0.01, 0.7, 0.5, 0.2)
)
ax.add_artist(first_legend)  # Add the first legend to the plot

# Add first legend for signal in upper right
second_legend = ax.legend(
    limit_handles, 
    limit_labels, 
    ncol=1, 
    loc="upper right",
    fontsize=fs-12,
    bbox_to_anchor=(0.47, 0.8, 0.5, 0.2)
)
ax.add_artist(second_legend)  # Add the first legend to the plot

# axis limits
ax.set_ylim([0.3, 1e3])
ax.set_xlim([1000,3000])

ax.set_xlabel(r"$m_{T^\prime}$ [GeV]",loc='right', fontsize=fs)
ax.tick_params(axis="both", which="major", labelsize=fs-4)

xticks = [1000, 1500, 2000, 2500, 3000]
ax.set_xticks(xticks)
ax.set_xticklabels([f"{x:.0f}" for x in xticks], rotation=0, fontsize=36)

# yticks = [1, 10, 100]
# ax.set_yticks(yticks)
# yticklabels = ['1','10',r'$10^2$']
# ax.set_yticklabels(yticklabels, rotation=0, fontsize=36)

hep.cms.label(loc=0, ax=ax, label='WiP', rlabel='', data=True, fontsize=fs)
lumiText = r"138 $fb^{-1}$ (13 TeV)"
hep.cms.lumitext(lumiText,ax=ax, fontsize=fs)

plt.savefig(f"plots/HiggsLimits_combined.pdf",bbox_inches='tight')
plt.savefig(f"plots/HiggsLimits_combined.png",bbox_inches='tight')