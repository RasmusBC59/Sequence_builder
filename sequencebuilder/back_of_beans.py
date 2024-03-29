import broadbean as bb
from qcodes.instrument.base import Instrument, Parameter
from broadbean.plotting import plotter
from typing import Dict, Optional, Sequence


class BagOfBeans(Instrument):
    """
    Class that turns a broadbean Sequence into a QCoDeS Intrument

        Parameters
        ----------
        seq (Parseq): Broadbean Sequence tured into a QCoDeS Parameter
        seq_path (str): Path to sequence file
        SR (float): sampling rate
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.add_parameter(name='seq',
                           label='Sequence',
                           parameter_class=ParSeq)
        self.add_parameter(name='seq_path',
                           label='Path to sequence file',
                           get_cmd=None,
                           set_cmd=None)
        self.add_parameter(name='SR',
                           label='sample rate',
                           unit='Hz',
                           initial_value=1.2e9,
                           parameter_class=sample_rate,
                           snapshot_exclude=True)
        self.add_parameter(name='amplitude',
                           label='Amplitude',
                           unit='V',
                           initial_value=4.5,
                           get_cmd=None,
                           set_cmd=None,
                           snapshot_exclude=True)


class ParSeq(Parameter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seq = bb.Sequence()

    def snapshot_base(
                      self, update: bool = False,
                      params_to_skip_update:
                      Optional[Sequence[str]] = None) -> Dict:
        return self.seq.description

    def get_raw(self):
        return self.seq

    def set_raw(self, newseq):
        self.seq = newseq

    def from_file(self):
        seq_path = self.root_instrument.seq_path()
        self.seq = bb.Sequence.init_from_json(seq_path)

    def to_file(self):
        seq_path = self.root_instrument.seq_path()
        self.seq.write_to_json(seq_path)

    def empty_sequence(self):
        SR = self.seq.SR
        self.seq = bb.Sequence()
        self.seq.setSR(SR)

    def set_all_channel_amplitude_offset(self,
                                         offset: float = 0) -> None:
        amplitude = self.root_instrument.amplitude.get()
        for chan in self.seq.channels:
            self.seq.setChannelAmplitude(chan, amplitude)
            self.seq.setChannelOffset(chan, offset)

    def number_of_elements(self):
        return len(self.seq.description.keys())-1

    def seq_settings_infinity_loop(self) -> None:
        """
        Play element 1 time and go to the next,
        except if you are the last element,
        then play 1 time and go to the first Element.
        """
        elementlist = list(self.seq.description.keys())[:-1]
        last_elem_nr = int(elementlist[-1])
        for elem_nr in elementlist:
            elem_nr = int(elem_nr)
            self.seq.setSequencingTriggerWait(elem_nr, 0)
            self.seq.setSequencingNumberOfRepetitions(elem_nr, 1)
            self.seq.setSequencingEventJumpTarget(elem_nr, 0)
            if elem_nr == last_elem_nr:
                self.seq.setSequencingGoto(elem_nr, 1)
            else:
                self.seq.setSequencingGoto(elem_nr, 0)

    def plot(self):
        plotter(self.seq)

    def plot_elem_nr(self, elem_nr):
        plotter(self.seq.element(elem_nr))


class sample_rate(Parameter):

    def get_raw(self):
        seq = self.root_instrument.seq()
        return seq.SR

    def set_raw(self, SR):
        seq = self.root_instrument.seq()
        seq.setSR(SR)
