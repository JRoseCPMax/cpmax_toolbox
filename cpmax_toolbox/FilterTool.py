from datetime import date
from typing import Optional
import pandas as pd
import numpy as np
import time
from rich.progress import track

def split_df(df:pd.DataFrame, split_col: str) -> dict:
    """
    splits a big DataFrame in a dict of multiple smaller ones\n
    works with pandas and dask
    """
    df_dict = {}
    keys = list(set(df[split_col]))
    for meas_id in keys:
        df_meas = df[df[split_col]==meas_id]
        if type(df) != pd.DataFrame:
            df_meas = df_meas.compute()
        df_dict[meas_id] = df_meas
    return df_dict


def to_vibA_import(df: pd.DataFrame, 
                   fnam: str, 
                   sample_rate: int, 
                   axis_dict: dict, 
                   scale: int=1,
                   mean: bool=False,
                   datestring:str=None, 
                   ) -> None:
    """
    Prepares a DataFrame for the Import in the vib.analyzer. \n

    ### Keyword Arguments:
    `df`          -- DataFrame containing the vib data\n
    `fnam`        -- output file name (should end on .txt)\n
    `sample_rate` -- sample rate of the vib data (used for f and p spectrum)\n
    `axis_dict`   -- which col in the DataFrame correspondes to which axis of the vibration\n
    `scale`       -- multiplier that is applied before the export\n
    `mean`        -- determines wether or not the mean value of each axis should be subtracted\n
    `datestring`  -- datetime string that gets written into the import file (%d.%m.%Y\\t%H:%M:%S format)\n

    """

    df = df.copy()

    if datestring == None:
        datestring = time.strftime('%d.%m.%Y\t%H:%M:%S', time.struct_time(time.localtime()))
    if set(axis_dict.values()) != {"Axial", "Radial", "Torsional", "Trigger"}:
        print("check axis_dict!")
        return
    
    df.rename(columns = axis_dict, inplace=True)
    with open(fnam, 'w') as f:
        f.write(f'Hardware-Takt:\t{sample_rate} Hz\n')
        f.write(f'Start der Messung:\t{datestring}\n\n')

    for ax in ["Axial", "Radial", "Torsional"]:
        df[ax] = scale*df[ax]
        if mean:
            df[ax] = df[ax]-df[ax].mean()

    df[['Axial', 'Radial', 'Torsional', 'Trigger']].to_csv(
        fnam, 
        sep='\t', 
        index=False, 
        mode = 'a'
        )


def cap_thres(df: pd.DataFrame, axis_list: list, thres: int, inplace: bool) -> Optional[pd.DataFrame]:
    """
    caps the maximum value of multiple axis, does not cut the time series

    ### Keyword Arguments:
    `df`        -- DataFrame containing the vib data \n
    `axis_list` -- list of column names containing the vib data \n
    `thres`     -- threshold to which the vib data is capped \n
    `inplace`   -- wether or not a new DataFrame should be returned or the existing DataFrame gets manipulated \n
    """

    if not inplace:
        df = df.copy()
    for ax in axis_list:
        s_abs = np.sqrt(df[ax]**2)
        s_sgn = -1 + 2*(df[ax]>0)
        s_thres = pd.Series(thres, index=s_sgn.index)
        df[ax] = s_sgn*np.minimum(s_thres, s_abs)
    if not inplace:
        return df


def filt_rot_thres(df: pd.DataFrame, axis_list: list, trig: str, thres: int, inplace: bool, debug:bool=None) -> Optional[pd.DataFrame]:
    """
    drops rotations from DataFrame where at least one of the axis hits the threshold

    ### Keyword Arguments:
    `df`        -- DataFrame containing the vib data \n
    `axis_list` -- list of column names containing the vib data \n
    `trig`      -- name of the rotation trigger column \n 
    `thres`     -- threshold at which the rotation is dropped \n
    `inplace`   -- wether or not a new DataFrame should be returned or the existing DataFrame gets manipulated \n

    """

    debug = False if debug==None else debug
    if debug:
        track_pb = track
    else:
        track_pb = lambda x:x

    if not inplace:
        df = df.copy()

    s_out = pd.Series(False, index=df.index)
    for ax in axis_list:
        s_out = s_out|(np.sqrt(df[ax]**2) > thres)

    s_rotstart = df[trig].diff()>0
    rot_starts = list(s_out[s_rotstart].index)
    rots = {(rot_starts[i], rot_starts[i+1]-1):0 for i in range(len(rot_starts)-1)}

    for (start, stop) in track_pb(rots.keys()):
        if any(s_out.loc[start:stop]):
           s_out.loc[start:stop] = True
        else:
           s_out.loc[start:stop] = False
    
    df = df[~s_out]

    if not inplace:
        return df


def filt_rot_mean(df: pd.DataFrame, axis_list: list, trig: str, diff: int, inplace: bool, debug:bool=None) -> Optional[pd.DataFrame]:
    """
    drops rotations from the DataFrame where the axis mean value differs more than `diff` from `0`

    ### Keyword Arguments: \n
    `df`        -- DataFrame containing the vib data \n
    `axis_list` -- list of column names containing the vib data \n
    `trig`      -- name of the rotation trigger column \n 
    `diff`      -- difference mean from 0 at which the rotation is dropped \n
    `inplace`   -- wether or not a new DataFrame should be returned or the existing DataFrame gets manipulated \n

    """

    debug = False if debug==None else debug
    if debug:
        track_pb = track
    else:
        track_pb = lambda x:x
    if not inplace:
        df = df.copy()

    s_rotstart = df[trig].diff()>0
    rot_starts = list(df[s_rotstart].index)
    rots = [(rot_starts[i], rot_starts[i+1]-1) for i in range(len(rot_starts)-1)]

    s_out = pd.Series(False, df.index)
    for (start, stop) in track_pb(rots):
        for ax in axis_list:
            if(abs(df.loc[start:stop, ax].mean())>diff):
                s_out.loc[start:stop] = True
                break
            else:
                s_out.loc[start:stop] = False

    df = df[~s_out]
    if not inplace:
        return df


if __name__ == "__main__":
    print("A package from cp.max Rotortechnik GmbH & Co. KG")
    print("maintained by Jonas Rose (j.rose@cpmax.com")