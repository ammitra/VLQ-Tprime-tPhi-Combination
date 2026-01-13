'''
Compare the hadronic and semileptonic channels for T > tH 
'''
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


# Individual results (B2G-22-001 and B2G-23-009) OBSERVED
B2G_22_001 = np.array([533.912606446475, 40.27359201144606, 25.16437256945517,30.85610480179935,30.941524694487136,26.607378475308707,22.037054927433825,16.87977483390729,13.95966283338852,15.565000624894477,11.242948802944115,9.959881335062384,10.235842064325476,9.329921430118166,8.704610043857048,8.109859824286733,8.046151076177573,7.86581949928322,7.874056174686013,7.857108786020054,8.055990200360498,8.180352315994078,8.172408868730468])
B2G_23_009 = np.array([111.59235984,  51.82023719,  29.1393809 ,  21.09403163,
        16.39941335,  10.87235659,   6.02779165,   4.04159538,
         3.01059824,   2.60975119,   2.27420451,   2.00587907,
         1.82171748,   1.63388171,   1.53273111,   1.4614648 ,
         1.36781367,   1.30498072,   1.2110743 ,   1.11966976,
         1.0456139 ])
# EXPECTED
B2G_22_001_exp = np.array([731.4998418627082, 96.24998241320321, 48.124991206601614,38.499994495133556,28.874993959034832,24.062495603300807,17.324997140347033,15.399997798053423,13.474996925907543,13.474996925907543,9.624998241320322,9.624998241320322,9.624998241320322,8.647459357436228,6.737498462953772,5.774998791806967,5.774998791806967,5.774998791806967,5.774998791806967,5.774998791806967,5.774998791806967,5.774998791806967,5.774998791806967])
B2G_23_009_exp = np.array([128.5842955112457, 48.7729981541633, 26.70712582767, 18.9873520284891, 15.920100733637799, 13.5450521484017, 9.067426435649299, 6.431879941374, 4.876160994172, 4.3437932617962, 3.9556259289383005, 3.3271613065153, 2.8224063571542, 2.3681479506194, 2.1122661419211997, 1.9437948940321002, 1.7868216382339, 1.6383039765059, 1.4881269307807, 1.3377306750043998, 1.2250895379111])


MTs = range(800,3100,100)

# 0-4 are m2,m1,exp,p1,p2 sigma limits, 5 is observed
limits = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}

tbqq_BR = 0.991 * 0.6732 # Wqq taken from https://arxiv.org/pdf/2201.07861
tblv_BR = 0.991 * 0.324
hbb_BR = 5.84E-1 # Hbb taken from table 11.3: https://pdg.lbl.gov/2016/

for MT in MTs:
    if MT >= 1000:
        # Combination
        f = ROOT.TFile.Open(f'combination/{MT}-125-tH/higgsCombine_{MT}-125-tH.AsymptoticLimits.mH120.root', 'READ')
    else:
        # B2G-22-001
        f = ROOT.TFile.Open(f'../Tprime/{MT}-125_unblind_fits/higgsCombine_{MT}-125_noCR_workspace.AsymptoticLimits.mH120.root', 'READ')
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
        # The B2G-23-009 input histograms are already normalized to this same xsec (and factoring in the t>blv VS t>bqq BR difference), so no need for additional corrections
        if (MT < 1400):
            norm = 0.1 * 1000.
        else:
            norm = 0.01 * 1000.

        lim = limit * factor * norm

        limits[i].append(lim)


for version in ['Supplementary', 'Final', 'Preliminary']:

    plt.style.use([hep.style.CMS])
    fig, ax = plt.subplots(figsize=(14,10), dpi=200)

    # Fontsize
    fs = 36
    # linewidth
    lw = 3.5

    # workaround for \mathcal
    plt.rcParams['mathtext.fontset'] = 'custom'
    plt.rcParams['mathtext.cal'] = 'stix:italic'

    # Confidence intervals
    CI68 = '#FFDF7Fff' 
    CI95 = '#85D1FBff'

    m2 = limits[0]
    m1 = limits[1]
    med = limits[2]
    p1 = limits[3]
    p2 = limits[4]
    obs = limits[5]


    ax.fill_between(MTs, m2, p2, color=CI95, label='95% expected')
    ax.fill_between(MTs, m1, p1, color=CI68, label='68% expected')
    ax.plot(MTs[2:], med[2:], color='black', linewidth=lw, linestyle='--', marker=None, label='Expected')
    ax.plot(MTs[2:], obs[2:], color='black', linewidth=lw, linestyle='-', marker=None, markersize=8, label='Observed', alpha=0.7)

    ax.set_ylabel(
        r'$\sigma(pp \to T^\prime bq)$ $\mathcal{B}(T^\prime \to tH(b\overline{b}))$ [fb]',
        fontsize=fs
    )

    # Theory cross sections directly from Francesco
    x1 = np.array([800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2200,2400,2600])
    x5 = np.array([800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,2000,2200,2400,2600])
    y1 = np.array([45.920,25.327,14.550,8.640,5.342,3.390,2.197,1.448,0.9743,0.6638,0.4588,0.3201,0.2256,0.119,0.0671,0.0401])
    y5 = np.array([218.437,120.4725,69.8805,42.0605,26.1005,16.6795,10.8675,7.239,4.894,3.366,2.3395,1.172,0.631556,0.36267,0.221838])


    # Individual results (observed)
    ax.plot(MTs,     B2G_22_001, color='#7a21dd', linewidth=lw, linestyle='solid', label=r'$H \to b\overline{b},\,t\to bq\overline{q}^\prime$''\n(this work)')
    ax.plot(MTs[2:], B2G_23_009, color='#e42536', linewidth=lw, linestyle='solid', label=r'$H \to b\overline{b},\,t\to b\ell\nu$''\n(arXiv:2510.25874)')

    # Individual results (expected)
    ax.plot(MTs,     B2G_22_001_exp, color='#7a21dd', linewidth=lw, linestyle='dashed')
    ax.plot(MTs[2:], B2G_23_009_exp, color='#e42536', linewidth=lw, linestyle='dashed')

    # # Plot the nominal theory xsecs for 1% and 5% width
    # theory1_c = '#7a21dd' 
    # theory5_c = '#e42536'
    # ax.plot(x1, y1, linewidth=lw, linestyle='solid', label=r'$\sigma(NLO),$ Singlet $T^{\prime},$ $\Gamma/m_{T^{\prime}}=$1%', color=theory1_c)
    # ax.plot(x5, y5, linewidth=lw, linestyle='solid', label=r'$\sigma(NLO),$ Singlet $T^{\prime},$ $\Gamma/m_{T^{\prime}}=$5%', color=theory5_c)

    # Re-plot the median expected and observed limits so they're above theory
    ax.plot(MTs[2:], med[2:], color='black', linewidth=lw, linestyle='--')
    ax.plot(MTs[2:], obs[2:], color='black', linewidth=lw, linestyle='-')

    # axis limits
    ylim=[0.4, 5e3]
    ax.set_ylim(ylim)
    ax.set_xlim([800, 3000]) # 800, 900 exclusive to B2G-22-001
    ax.set_yscale('log')

    ax.set_xlabel(r"$m_{T^\prime}$ [GeV]",loc='right', fontsize=fs)
    ax.tick_params(axis="both", which="major", labelsize=fs-4)

    xticks = [1000, 1500, 2000, 2500, 3000]
    ax.set_xticks(xticks)
    ax.set_xticklabels([f"{x:.0f}" for x in xticks], rotation=0, fontsize=36)

    # Legend stuff 
    channel_handles = []
    channel_labels  = []
    limit_handles  = []
    limit_labels   = []
    handles, labels = ax.get_legend_handles_labels()
    for handle, label in zip(handles, labels):
        if 'overline' in label:
            channel_handles.append(handle)
            channel_labels.append(label)
        else:
            limit_handles.append(handle)
            limit_labels.append(label)

    from matplotlib.lines import Line2D
    channel_handles.insert(0, Line2D([0], [0], color='black', lw=lw, alpha=0.7))
    channel_labels.insert(0, 'Combination')

    # Now place the legends
    # Add first legend for channels in upper right
    first_legend = ax.legend(
        channel_handles, 
        channel_labels, 
        ncol=1, 
        loc="upper left",
        fontsize=fs-10,
        bbox_to_anchor=(0.1, 0.79, 0.5, 0.2)
    )
    ax.add_artist(first_legend)  # Add the first legend to the plot

    # Add first legend for limits in upper right
    second_legend = ax.legend(
        limit_handles[::-1], 
        limit_labels[::-1], 
        ncol=1, 
        loc="upper right",
        fontsize=fs-10,
        bbox_to_anchor=(0.42, 0.7, 0.5, 0.2)
    )
    ax.add_artist(second_legend)  # Add the first legend to the plot

    ax.text(0.75, 0.95, r'95% CL upper limit', ha='center', va='top', fontsize=fs-7, transform=ax.transAxes, fontproperties='Tex Gyre Heros')


    label = version if version != 'Final' else ''
    hep.cms.label(loc=0, ax=ax, label=label, rlabel='', data=True, fontsize=fs)
    lumiText = r"138 $fb^{-1}$ (13 TeV)"
    hep.cms.lumitext(lumiText,ax=ax, fontsize=fs)


    plt.savefig(f"plots/HiggsLimits_combined_PLB_comparison_{version}.pdf",bbox_inches='tight')
    plt.savefig(f"plots/HiggsLimits_combined_PLB_comparison_{version}.png",bbox_inches='tight')
