l = []

mask = False

for region in ['S','V']:
    for i in range(1,5):
        for part in ['muon','electron']:
            l.append(f'mask_Name2_{region}{i}_{part}={0 if not mask else 1}')

print(','.join(l))