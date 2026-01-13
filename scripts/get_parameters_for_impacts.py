'''
Prints all the nuisance parameters to scan for impacts plot
'''
import ROOT

def _tolist(argset):
    return [x.GetName() for x in argset]

def getParameters():
    """Get nuisance parameters from workspace"""
    f = ROOT.TFile.Open('combination/1800-125-tH/workspace_masked.root','READ')
    w = f.Get("w")
    ps = _tolist(w.allVars())
    pois = _tolist(w.set("ModelConfig_POI"))
    obs = _tolist(w.genobj("ModelConfig").GetObservables())

    ret_ps = []
    for p in ps:
        if not (
            "mcstat" in p
            or "qcdparam" in p
            or p.endswith(("_In", "__norm"))
            or p.startswith(("n_exp_", "mask_"))
            or p in pois
            or p in obs
            or 'ttbar' in p
            or 'DAK' in p
            or p == 'ZERO'
            or p == 'ONE'
            or p == '_zero_'
            or 'Background_VR' in p
            or p == 'MH'
            or p == 'MHWW'
            or '_bin_' in p
            or 'Trigger' in p
        ):
            ret_ps.append(p)

    return ret_ps

params = getParameters()
print(f'there are {len(params)} params:\n')
print(' '.join(params))

