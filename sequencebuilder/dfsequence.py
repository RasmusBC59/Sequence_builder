
import broadbean as bb
import numpy as np


ramp = bb.PulseAtoms.ramp


def df_to_seq(df, divider, seg_mode_trig=False, int_to_zero=False, scale= 1e-3, timescale=1e-6, marker_time_dic=None, SR=1.2e9):
    seq = bb.Sequence()
    nr_elem = find_recurcive(df)
    chan_list = find_channels(df)
    max_time = sum([smart_max(list_or_sting(t[0])) for t in df[['time']].values])*timescale
    id = df.index.values
    idnr = id.shape[0]
    for h in range(nr_elem):
        elem = bb.Element()
        for ch in chan_list:
            div = divider[ch]*scale
            chnr = int(ch[2:])
            bp = bb.BluePrint()
            bp.setSR(SR)
            for i in range(idnr):
                nm = df.iloc[i][['name']].values[0]
                volt = df.iloc[i][[ch]].values[0]
                volt = getvoltvalues(volt, h, div)
                dr = df.iloc[i][['time']].values[0]
                dr = get_time(dr, h)*timescale
                bp.insertSegment(i, ramp, volt, name=nm, dur=dr)
                add_marker(bp, df, i, chnr, 1, nm, dr, marker_time_dic)
                add_marker(bp, df, i, chnr, 2, nm, dr, marker_time_dic)
                if chnr == 2 and h == 0 and seg_mode_trig and i == 0:
                    mktime = marker_time(marker_time_dic, dr, chnr, 1)
                    bp.setSegmentMarker(nm, (0.0, mktime), 1)
            if int_to_zero:
                bp = bp_int_to_zero(bp, max_time)
            elem.addBluePrint(chnr, bp)
        seq.addElement(h+1, elem)
    seq.setSR(SR)
    
    return seq


def add_marker(bp, df, i, chnr, mnr, nm, dr, marker_time_dic):
    if df.iloc[i][[f'm{chnr}{mnr}']].values[0]:
        mktime = marker_time(marker_time_dic, dr, chnr, mnr)
        bp.setSegmentMarker(nm, (0, mktime), mnr)


def marker_time(marker_time_dic, dr, chnr, mnr):
    if marker_time_dic:
        if marker_time_dic[f'm{chnr}{mnr}']:
            return marker_time_dic[f'm{chnr}{mnr}']
    return dr


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
    if ln == []:
        return 1
    [x for x in ln if x == ln[0]] == ln
    return ln[0]


def find_channels(df):
    return [ch for ch in df.columns.values if 'ch' in ch]


def getvoltvalues(volt, i=None, divider=1):
    if isinstance(volt, (int, float)):
        return (volt*divider, volt*divider)
    elif type(volt) in (list, str):
        volt = list_or_sting(volt)
        if len(volt) == 2:
            return tuple(np.array(volt)*divider)
        elif len(volt) == 3:
            values = np.linspace(*volt, endpoint=True)
            return (values[i]*divider, values[i]*divider)
        elif len(volt) == 1:
            return (float(volt[0])*divider, float(volt[0])*divider)


def get_time(t, i=None):
    if type(t) in (list, str):
        t = list_or_sting(t)
        if len(t) > 1:
            values = np.linspace(*t, endpoint=True)
            return values[i]
        else:
            return float(t[0])
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
        val = strtolist(val)
    return val


def strtolist(s):
    s = s.replace('[', '')
    s = s.replace(']', '')
    values = [float(i) for i in s.split(',')]
    if len(values) == 3:
        values[-1] = int(values[-1])
    return values

def smart_max(x):
    if type(x) in (int, float, np.int64, np.float64):
        return x
    if len(x)==3:
        x.pop()
    return max(x)


def bp_int_to_zero(bp, time):
    num_seg = number_of_segments(bp)
    tottime = 0
    tottimevolt = 0
    for i in range(num_seg):
        pulsestart = bp.description['segment_%02d'%(i+1)]['arguments']['start']
        pulsestop = bp.description['segment_%02d'%(i+1)]['arguments']['stop']
        pulsedur = bp.description['segment_%02d'%(i+1)]['durations']
        tottime += pulsedur
        tottimevolt += pulsedur*(pulsestart+pulsestop)/2
    timeD = time*1.65 - tottime
    voltD = -tottimevolt/timeD


    bp.insertSegment(num_seg, ramp, (voltD, voltD),
                        name='CorretD', dur=timeD)
    return bp

def number_of_segments(bp):
    nr = len(bp.description)-4
    return nr
