
import broadbean as bb
import numpy as np


ramp = bb.PulseAtoms.ramp


def df_to_seq(df,seg_mode_trig=False):
    seq = bb.Sequence()
    nr_elem = find_recurcive(df)
    chan_list = find_channels(df)
    id = df.index.values
    idnr = id.shape[0]
    for h in range(nr_elem):
        elem = bb.Element()
        for ch in chan_list:
            chnr = int(ch[2:])
            bp = bb.BluePrint()
            bp.setSR(1.2e9)
            for i in range(idnr):
                nm = df.iloc[i][['name']].values[0]
                volt = df.iloc[i][[ch]].values[0]
                volt = getvoltvalues(volt, h)
                dr = df.iloc[i][['time']].values[0]
                dr = get_time(dr, h)*1e-6
                bp.insertSegment(i, ramp, volt, name=nm, dur=dr)
                add_marker(bp, df, i, chnr, 1, nm, dr)
                add_marker(bp, df, i, chnr, 2, nm, dr)
                if chnr == 2 and h == 0 and seg_mode_trig and i == 0:
                    bp.setSegmentMarker(nm, (0.0, 0.5e-6), 1)
            elem.addBluePrint(chnr, bp)
        seq.addElement(h+1, elem)
    seq.setSR(1.2e9)
    return seq


def add_marker(bp, df, i, chnr, mnr, nm, dr):
    if df.iloc[i][[f'm{chnr}{mnr}']].values[0]:
        bp.setSegmentMarker(nm, (0, dr), mnr)


def find_recurcive(df):
    col_to_tjek = find_channels(df)
    col_to_tjek.append('time')
    list_of_lists = []
    for col in col_to_tjek:
        list_of_lists += [list_or_sting(x) for x in df[col].values
                          if type(x) in [list, str]
                          and len(list_or_sting(x)) == 3]
    ln = []
    for li in list_of_lists:
        ln.append(int(li[-1]))
    [x for x in ln if x == ln[0]] == ln
    return ln[0]


def find_channels(df):
    return [ch for ch in df.columns.values if 'ch' in ch]


def getvoltvalues(volt, i=None):
    if isinstance(volt, (int, float)):
        return (volt, volt)
    elif type(volt) in (list, str):
        volt = list_or_sting(volt)
        if len(volt) == 2:
            return tuple(volt)
        elif len(volt) == 3:
            values = np.linspace(*volt, endpoint=True)
            return (values[i], values[i])


def get_time(t, i=None):
    if type(t) in (list, str):
        t = list_or_sting(t)
        values = np.linspace(*t, endpoint=True)
        return values[i]
    else:
        return t


def iflistorstr(val):
    if type(val) in (list, str):
        val = list_or_sting(val)
        return val
    else:
        return val


def list_or_sting(val):
    if type(val) == str:
        return strtolist(val)
    else:
        return val


def strtolist(s):
    values = [float(i) for i in s.split(',')]
    if len(values) == 3:
        values[-1] = int(values[-1])
    return values
