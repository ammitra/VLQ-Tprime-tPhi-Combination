'''
Script to generate the csv for the combined limits.
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

firstrow = 'MT,MP,m2,m1,exp,p1,p2,obs\n'
rows = []

for MT in MTs:
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
        vals = []
        for i in range(6):  # 0:m2, 1:m1, 2:exp, 3:p1, 4:p2, 5:obs
            limTree.GetEntry(i) # obs
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
            vals.append(str(lim))
        # now create the next row
        row = f'{MT},{MP},{",".join(vals)}\n'
        rows.append(row)

print('Writing limits to file...')
with open('limits/combination_limits.csv','w') as f:
    f.write(firstrow)
    for row in rows:
        f.write(row)

