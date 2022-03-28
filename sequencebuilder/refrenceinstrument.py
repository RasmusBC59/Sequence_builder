import numpy as np
from qcodes.utils.validators import Numbers, Arrays
from qcodes.instrument.parameter import ParameterWithSetpoints, Parameter
from typing import Iterable, Union
from sequencebuilder.spinbuilder import AWGController


class AlazarInstrument(AWGController):

    def __init__(self, name, awg=None, data_func=None,
                 n_points=100,  **kwargs):

        super().__init__(name, awg, **kwargs)
        self.data_func = data_func
        self.dis_tabs = None

        self.add_parameter('n_points',
                           unit='',
                           initial_value=n_points,
                           vals=Numbers(1, 200),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('V_dc',
                           initial_value=0,
                           unit='V',
                           label='V_dc',
                           vals=Numbers(-1, 1),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('V_start',
                           initial_value=0,
                           unit='V',
                           label='V_start',
                           vals=Numbers(-1, 1),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('V_stop',
                           initial_value=0.1,
                           unit='V',
                           label='V_stop',
                           vals=Numbers(-1, 1),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('V_axis',
                           unit='V',
                           label='V Axis',
                           parameter_class=DFSetPoints,
                           vals=Arrays(shape=(self.n_points.get_latest,)))

        self.add_parameter('data',
                           unit='mV',
                           setpoints=(self.V_axis,),
                           label='V',
                           parameter_class=AlazarData,
                           data_func=self.data_func,
                           vals=Arrays(shape=(self.n_points.get_latest,)))

        self.add_parameter('datarefrence',
                           unit='V',
                           setpoints=(self.V_axis,),
                           label='V',
                           parameter_class=Refrece,
                           data_func=self.data_func,
                           vals=Arrays(shape=(self.n_points.get_latest,)))

    def updata_setpoints(self):
        time_recurcive = self.get_recurcive('time')

        if len(time_recurcive) == 1:
            time_setpoint = np.linspace(*time_recurcive[0], endpoint=True)
            self.n_points.set(time_recurcive[0][2])
            return time_setpoint

        chx_recurcive = self.get_recurcive(f'ch{self.ch_x}')
        chy_recurcive = self.get_recurcive(f'ch{self.ch_y}')

        if len(chx_recurcive) == 1 and len(chy_recurcive) == 1:
            vec_list = list(zip(np.linspace(*chx_recurcive[0], endpoint=True),
                            np.linspace(*chy_recurcive[0], endpoint=True)))
            norm_list = [np.sqrt(x[0]**2+x[1]**2) for x in vec_list]
            self.n_points.set(chx_recurcive[0][2])
            return norm_list

        elif len(chx_recurcive) == 1:
            self.n_points.set(chx_recurcive[0][2])
            return np.linspace(*chx_recurcive[0], endpoint=True)

        elif len(chy_recurcive) == 1:
            self.n_points.set(chy_recurcive[0][2])
            return np.linspace(*chy_recurcive[0], endpoint=True)

    def get_recurcive(self, dim_name):
        recurcive_info = self.get_recurcive_info(dim_name)
        return [x for x in recurcive_info if x]


class GeneratedSetPoints(Parameter):
    """
    A parameter that generates a setpoint array from start, stop and num points
    parameters.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()

    def set_raw(self, value: Iterable[Union[float, int]]) -> None:
        self.sweep_array = value

    def get_raw(self):
        return self.sweep_array

    def reset(self):
        V_dc = self.instrument.V_dc.get()
        V_start = self.instrument.V_start.get() + V_dc
        V_stop = self.instrument.V_stop.get() + V_dc
        nr = self.instrument.n_points.get()
        self.sweep_array = np.linspace(V_start, V_stop, nr, endpoint=True)


class AlazarData(ParameterWithSetpoints):

    def __init__(self, data_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_func = data_func

    def get_raw(self):

        return self.data_func()


class Refrece(ParameterWithSetpoints):

    def __init__(self, data_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_func = data_func

    def get_raw(self):
        datatotal = self.data_func()
        datameas = datatotal[::2]
        dataref = datatotal[1::2]

        return datameas-dataref


class DFSetPoints(Parameter):
    """
    A parameter that generates a setpoint from a df
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()

    def set_raw(self, value: Iterable[Union[float, int]]) -> None:
        self.sweep_array = value

    def get_raw(self):
        return self.sweep_array

    def reset(self):
        self.sweep_array = self.instrument.updata_setpoints()
