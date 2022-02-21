
import broadbean as bb
import numpy as np
import numpy as np
import pandas as pd
import panel as pn

#pn.extension('tabulator')
import matplotlib.pyplot as plt

ramp = bb.PulseAtoms.ramp


def strtolist(s):
    values = [float(i) for i in s.split(',')]
    if len(values) == 3:
        values[-1] = int(values[-1]) 
    return values


def list_or_sting(val):
    if type(val) == str:
        return strtolist(val)
    else:
        return val


def iflistorstr(val):
    if type(val) in (list, str):
        val = list_or_sting(val)
        return val
    else:
        return val


def getvoltvalues(volt, i=None):
    print('type', type(volt), i, volt)
    if isinstance(volt, (int, float)):
        print('hep')
        return (volt, volt)
    elif type(volt) in (list, str):
        volt = list_or_sting(volt)
        if len(volt) == 2:
            return tuple(volt)
        elif len(volt) == 3:
            values = np.linspace(*volt, endpoint=True)
            return (values[i],values[i])


def get_time(t, i=None):
    #print('type', type(t))
    #print(t)
    if type(t) in (list, str):
        t = list_or_sting(t)
        values = np.linspace(*t, endpoint=True)
        return values[i]
    else:
        return t


def find_channels(df):
    return [ch for  ch in df.columns.values if 'ch' in ch]


def find_recurcive(df):
    col_to_tjek  = find_channels(df)
    col_to_tjek.append('time') 
    bla = []
    for col in col_to_tjek: 
        bla += [list_or_sting(x)  for x in df[col].values if type(x) in [list,str] and len(list_or_sting(x)) == 3]
    ln = []
    for l in bla:
        ln.append(int(l[-1]))
    [x for x in ln if x==ln[0]] == ln
    return ln[0] 


def df_to_seq(df):
    seq = bb.Sequence()
    nr_elem = find_recurcive(df)
    chan_list = find_channels(df)
    id = df.index.values
    idnr = id.shape[0]
    for h in range(nr_elem):
        elem = bb.Element()
        for ch in chan_list:
            bp = bb.BluePrint()
            bp.setSR(1.2e9)
            for i in range(idnr):
                nm = df.iloc[i][['name']].values[0]
                volt = df.iloc[i][[ch]].values[0]
                volt = getvoltvalues(volt, h)
                dr = df.iloc[i][['time']].values[0]
                dr = get_time(dr, h)*1e-6
                bp.insertSegment(i, ramp, volt, name=nm, dur=dr)
            chnr = int(ch[2:])
            elem.addBluePrint(chnr, bp)
        seq.addElement(h+1, elem)
    seq.setSR(1.2e9)
    return seq
