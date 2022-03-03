
from qcodes import Parameter
import numpy as np
from qcodes.utils.validators import Numbers, Arrays
from qcodes.instrument.base import Instrument
from qcodes.instrument.channel import InstrumentChannel
from qcodes.instrument.parameter import ParameterWithSetpoints, Parameter
from typing import Any, Iterable, Tuple, Union

class GeneratedSetPoints(Parameter):
    """
    A parameter that generates a setpoint array from start, stop and num points
    parameters.
    """
    def __init__(self,*args, **kwargs):
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



class AlazarInstrument(Instrument):

    def __init__(self, name, data_func, n_points,  **kwargs):

        super().__init__(name, **kwargs)
        self.data_func = data_func
        self.dis_tabs = None

        self.add_parameter('n_points',
                           unit='',
                           initial_value=n_points,
                           vals=Numbers(1,200),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('V_dc',
                           initial_value=0,
                           unit='V',
                           label='V_dc',
                           vals=Numbers(-1,1),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('V_start',
                           initial_value=0,
                           unit='V',
                           label='V_start',
                           vals=Numbers(-1,1),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('V_stop',
                           initial_value=0.1,
                           unit='V',
                           label='V_stop',
                           vals=Numbers(-1,1),
                           get_cmd=None,
                           set_cmd=None)
        
        self.add_parameter('V_axis',
                           unit='V',
                           label='V Axis',
                           parameter_class=GeneratedSetPoints,
                           vals=Arrays(shape=(self.n_points.get_latest,)))

        self.add_parameter('data',
                           unit='V',
                           setpoints=(self.V_axis,),
                           label='V',
                           parameter_class=AlazarData,
                           data_func = self.data_func,
                           vals=Arrays(shape=(self.n_points.get_latest,)))

        self.add_parameter('datarefrence',
                           unit='V',
                           setpoints=(self.V_axis,),
                           label='V',
                           parameter_class=Refrece,
                           data_func = self.data_func,
                           vals=Arrays(shape=(self.n_points.get_latest,)))

            




            

        