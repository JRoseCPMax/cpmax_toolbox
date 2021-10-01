#%%
import cpmaxToolbox as cpm
# import cpmaxToolbox as cpm
import pandas as pd
import time
from rich.progress import track
import os

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
    plt.plot(df.index, df.ax)
    df = cpm.filt_rot_thres(df, ["ax", "ay", "az"], "Trigger", 0.5, False)
    plt.plot(df.index, df.ax)

    cpm.to_vibA_import(df, fnam, int(fs), axis_dict, scale, True, l0)

    plt.show()


import matplotlib.pyplot as plt
plt.plot(df.ax)
plt.show()
