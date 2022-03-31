from qcodes.dataset import load_by_run_spec
import holoviews as hv
from holoviews import streams

hv.extension('bokeh')


class DrawPulseOnPlot():
    def __init__(self, id):
        self.id = id   
        self.tap = streams.SingleTap(transient=True)
        self.double_tap = streams.DoubleTap(rename={'x': 'x2', 'y': 'y2'},
                                            transient=True)
        self.taps = []

    def record_taps(self, x, y, x2, y2):
        if None not in [x, y]:
            self.taps.append((x, y, 1))
        elif None not in [x2, y2]:
            self.taps.append((x2, y2, 2))
        pointplot = hv.Points(self.taps,
                              vdims='Taps').opts(color='Taps',
                                                 cmap={1: 'red', 2: 'gray'},
                                                 size=10,
                                                 tools=['hover'])
        curveplot = hv.Curve([x[:-1] for x in self.taps])
        return pointplot*curveplot

    def pulse_from_plot(self):
        data = load_by_run_spec(captured_run_id=self.id)
        df = data.to_pandas_dataframe()
        vdims = tuple(df.columns.values)
        df2 = df.reset_index()
        data_plot = hv.Points(df2, vdims=vdims[0]).opts(color=vdims[0], colorbar=True, size=10)
        return data_plot

    def start_plot(self):
        self.taps_dmap = hv.DynamicMap(self.record_taps, streams=[self.tap, self.double_tap])
        return self.pulse_from_plot()*self.taps_dmap
