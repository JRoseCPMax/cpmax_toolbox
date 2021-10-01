#%%
import os
os.system("py -3 -m pip install -i https://test.pypi.org/simple/ cpmaxToolbox")
#%%
import cpmaxToolbox as cpm
import pandas as pd
import time
from rich.progress import track


t_format_iso = '%Y-%m-%dT%H:%M:%S'
t_format_de  = '%d.%m.%Y\t%H:%M:%S'
scale = 1000

axis_dict = {'ax':'Radial','ay':'Torsional','az':'Axial', "Trigger":"Trigger"}

#%%
for fnam in track([f for f in os.listdir() if f.endswith('.csv')]):
    with open(fnam) as f:
        l0 = f.readline()[:-1]
    t = time.strptime(l0, t_format_iso)
    l0 = time.strftime(t_format_de, t)

    df = pd.read_csv(fnam, skiprows=15)
    fs = 1e3/(df['millis'].diff().median())
    fnam = 'Import_'+fnam
    fnam = fnam.replace('.csv', '.txt')
    print(len(df))
    df_2 = cpm.filt_rot_thres(df, ["ax", "ay", "az"], "Trigger", 0.5, True, False)
    print(len(df))
    # cpm.to_vibA_import(df, fnam, int(fs), axis_dict, scale, True, l0)

#%%
# %matplotlib qt
import matplotlib.pyplot as plt
plt.plot(df.ax)
plt.show()
# %%
