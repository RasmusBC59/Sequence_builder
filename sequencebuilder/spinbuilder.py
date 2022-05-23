from xmlrpc.client import Boolean
import broadbean as bb
import pandas as pd
import string
import numpy as np
from sequencebuilder.back_of_beans import BagOfBeans
from sequencebuilder.dfsequence import df_to_seq
from sequencebuilder.dfsequence import list_or_sting
import time
ramp = bb.PulseAtoms.ramp


class SpinBuilder(BagOfBeans):

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.df = None
        self.ch_x = 1
        self.ch_y = 2
        self.divider = {f'ch{self.ch_x}': 1, f'ch{self.ch_y}': 1}
        self.scale = 1e-3
        self.timescale = 1e-6
        self.zero_point = (0, 0)
        self.hp_frequency = None
        self.marker_time_dic = {f'm{self.ch_x}1': 0, f'm{self.ch_x}2': 0,
                                f'm{self.ch_y}1': 500e-9, f'm{self.ch_y}2': 0}
        self.spinfunnel()

    def seq_from_df(self, seg_mode_trig: Boolean = True, int_to_zero: Boolean = True):
        self.seq.seq = df_to_seq(self.df, self.divider, seg_mode_trig=seg_mode_trig,
                                 int_to_zero=int_to_zero, scale=self.scale,
                                 timescale=self.timescale,
                                 marker_time_dic=self.marker_time_dic,
                                 SR=self.SR())

        self.seq.set_all_channel_amplitude_offset(amplitude=4.5, offset=0)
        self.seq.seq_settings_infinity_loop()
        if self.hp_frequency:
            self.seq.seq.setChannelFilterCompensation(channel=self.ch_x,
                                                      kind='HP', order=1,
                                                      f_cut=self.hp_frequency)
            self.seq.seq.setChannelFilterCompensation(channel=self.ch_y,
                                                      kind='HP', order=1,
                                                      f_cut=self.hp_frequency)

    def spinfunnel(self):
        self.df = pd.DataFrame({
                                'name': ['a', 'b', 'c', 'eta', 'read', 'd', 'refrence'],
                                'time': [1, 1, 1, 1, 1, 1, 1],
                                'type': ['ramp', 'ramp', 'ramp', 'ramp', 'ramp', 'ramp', 'ramp'],
                                f'ch{self.ch_x}': [0.0, [0.0, 0.25], 0.25, [0.25, -0.2, 100], 0.25, [0.25, 0.28], 0.28],
                                f'ch{self.ch_y}': [0.0, [0.0, 0.25], 0.25, [0.25, -0.2, 100], 0.25, [0.25, 0.28], 0.28],
                                f'm{self.ch_x}1': [False, False, False, False, True, False, False],
                                f'm{self.ch_y}1': [False, False, False, False, False, False, False],
                                f'm{self.ch_x}2': [False, False, False, False, False, False, False],
                                f'm{self.ch_y}2': [False, False, False, False, False, False, False]
                                }, index=[1, 2, 3, 4, 5, 6, 7])
        self.seq_from_df()

    def spin_funnel_seq(self, a1, a2, a3, eta, readout, a5, a6):

        self.seq.empty_sequence()
        len_eta = len(eta[0])
        for i in range(len_eta):
            elem = bb.Element()
            bp = self.spin_funnel_blue_print((a1[0], a1[2]), (a2[0], a2[2]), (a3[0], a3[2]),
                                             (eta[0][i], eta[2]), (readout[0], readout[2]), (a5[0], a5[2]), (a6[0], a6[2]))
            bp.setSegmentMarker('readout', (0.0, 0.5e-6), 1)
            bp = self.bp_int_to_zero(bp)

            bp2 = self.spin_funnel_blue_print((a1[1], a1[2]), (a2[1], a2[2]), (a3[1], a3[2]),
                                              (eta[1][i], eta[2]), (readout[1], readout[2]), (a5[1], a5[2]), (a6[1], a6[2]))
            bp2 = self.bp_int_to_zero(bp2)
            if i == 0:
                bp2.setSegmentMarker('aa', (0.0, 0.5e-6), 1)
            bp.setSR(self.SR())
            bp2.setSR(self.SR())
            elem.addBluePrint(1, bp)
            elem.addBluePrint(2, bp2)
            self.seq.seq.addElement(i+1, elem)
            self.seq.seq.setSR(self.SR())
            self.seq.set_all_channel_amplitude_offset(amplitude=4.5, offset=0)
            self.seq_settings_infinity_loop(i+1, len_eta)

    def exchange_seq_oneD(self, a1, a2, a3, a4, eta, a5, a6, a7,
                          readout, a8, a9):

        self.seq.empty_sequence()
        len_eta = len(eta[2])
        for i in range(len_eta):
            elem = bb.Element()
            bp = self.spin_exchange_blue_print((a1[0], a1[2]),
                                               (a2[0], a2[2]),
                                               (a3[0], a3[2]),
                                               (a4[0], a4[2]),
                                               (eta[0], eta[2][i]),
                                               (a5[0], a5[2]),
                                               (a6[0], a6[2]),
                                               (a7[0], a7[2]),
                                               (readout[0], readout[2]),
                                               (a8[0], a8[2]),
                                               (a9[0], a9[2]))
            bp.setSegmentMarker('readout', (0.0, 0.5e-6), 1)
            bp = self.bp_int_to_zero(bp)

            bp2 = self.spin_exchange_blue_print((a1[1], a1[2]),
                                                (a2[1], a2[2]),
                                                (a3[1], a3[2]),
                                                (a4[1], a4[2]),
                                                (eta[1], eta[2][i]),
                                                (a5[1], a5[2]),
                                                (a6[1], a6[2]),
                                                (a7[1], a7[2]),
                                                (readout[1], readout[2]),
                                                (a8[1], a8[2]),
                                                (a9[1], a9[2]))
            bp2 = self.bp_int_to_zero(bp2)
            if i == 0:
                bp2.setSegmentMarker('aa', (0.0, 0.5e-6), 1)
            bp.setSR(self.SR())
            bp2.setSR(self.SR())
            elem.addBluePrint(1, bp)
            elem.addBluePrint(2, bp2)
            self.seq.seq.addElement(i+1, elem)
            self.seq.seq.setSR(self.SR())
            self.seq.set_all_channel_amplitude_offset(amplitude=4.5, offset=0)
            self.seq_settings_infinity_loop(i+1, len_eta)

    def dephasing_seq(self, a1, eta, readout, a8, a9):

        self.seq.empty_sequence()
        len_eta = len(eta[2])
        for i in range(len_eta):
            elem = bb.Element()
            bp = self.spin_dephasing_blue_print((a1[0], a1[2]),
                                                (eta[0], eta[2][i]),
                                                (readout[0], readout[2]),
                                                (a8[0], a8[2]),
                                                (a9[0], a9[2]))
            bp.setSegmentMarker('readout', (0.0, 0.5e-6), 1)
            bp = self.bp_int_to_zero(bp)

            bp2 = self.spin_dephasing_blue_print((a1[1], a1[2]),
                                                 (eta[1], eta[2][i]),
                                                 (readout[1], readout[2]),
                                                 (a8[1], a8[2]),
                                                 (a9[1], a9[2]))
            bp2 = self.bp_int_to_zero(bp2)
            if i == 0:
                bp2.setSegmentMarker('aa', (0.0, 0.5e-6), 1)
            bp.setSR(self.SR())
            bp2.setSR(self.SR())
            elem.addBluePrint(1, bp)
            elem.addBluePrint(2, bp2)
            self.seq.seq.addElement(i+1, elem)
            self.seq.seq.setSR(self.SR())
            self.seq.set_all_channel_amplitude_offset(amplitude=4.5, offset=0)
            self.seq_settings_infinity_loop(i+1, len_eta)

    def exchange_seq_oneD_volt(self, a1, a2, a3, a4, eta, a5, a6, a7,
                               readout, a8, a9):

        self.seq.empty_sequence()
        len_eta = len(eta[0])
        for i in range(len_eta):
            elem = bb.Element()
            bp = self.spin_exchange_blue_print((a1[0], a1[2]),
                                               (a2[0], a2[2]),
                                               (a3[0], a3[2]),
                                               (a4[0], a4[2]),
                                               (eta[0][i], eta[2]),
                                               (a5[0], a5[2]),
                                               (a6[0], a6[2]),
                                               (a7[0], a7[2]),
                                               (readout[0], readout[2]),
                                               (a8[0], a8[2]),
                                               (a9[0], a9[2]))
            bp.setSegmentMarker('readout', (0.0, 0.5e-6), 1)
            bp = self.bp_int_to_zero(bp)

            bp2 = self.spin_exchange_blue_print((a1[1], a1[2]),
                                                (a2[1], a2[2]),
                                                (a3[1], a3[2]),
                                                (a4[1], a4[2]),
                                                (eta[1][i], eta[2]),
                                                (a5[1], a5[2]),
                                                (a6[1], a6[2]),
                                                (a7[1], a7[2]),
                                                (readout[1], readout[2]),
                                                (a8[1], a8[2]),
                                                (a9[1], a9[2]))
            bp2 = self.bp_int_to_zero(bp2)
            if i == 0:
                bp2.setSegmentMarker('aa', (0.0, 0.5e-6), 1)
            bp.setSR(self.SR())
            bp2.setSR(self.SR())
            elem.addBluePrint(1, bp)
            elem.addBluePrint(2, bp2)
            self.seq.seq.addElement(i+1, elem)
            self.seq.seq.setSR(self.SR()())
            self.seq.set_all_channel_amplitude_offset(amplitude=4.5, offset=0)
            self.seq_settings_infinity_loop(i+1, len_eta)

    def spin_funnel_blue_print(self, a1, a2, a3, eta, readout, a5, a6):
        bp = bb.BluePrint()
        bp.insertSegment(0, ramp, (a1[0], a1[0]), name='aa', dur=a1[1])
        bp.insertSegment(1, ramp, (a1[0], a2[0]), name='ab', dur=a2[1])
        bp.insertSegment(2, ramp, (a3[0], a3[0]), name='ac', dur=a3[1])
        bp.insertSegment(3, ramp, (eta[0], eta[0]), name='eta', dur=eta[1])
        bp.insertSegment(4, ramp, (readout[0], readout[0]), name='readout', dur=readout[1])
        bp.insertSegment(5, ramp, (readout[0], a5[0]), name='ad', dur=a5[1])
        bp.insertSegment(6, ramp, (a6[0], a6[0]), name='ae', dur=a6[1])
        return bp

    def spin_exchange_blue_print(self, a1, a2, a3, a4, eta, a5, a6, a7,
                                 readout, a8, a9):
        bp = bb.BluePrint()
        bp.insertSegment(0, ramp, (a1[0], a1[0]), name='aa', dur=a1[1])
        bp.insertSegment(1, ramp, (a1[0], a2[0]), name='ab', dur=a2[1])
        bp.insertSegment(2, ramp, (a2[0], a3[0]), name='ac', dur=a3[1])
        bp.insertSegment(3, ramp, (a4[0], a4[0]), name='ad', dur=a4[1])
        bp.insertSegment(4, ramp, (eta[0], eta[0]), name='eta', dur=eta[1])
        bp.insertSegment(5, ramp, (a5[0], a5[0]), name='ae', dur=a5[1])
        bp.insertSegment(6, ramp, (a5[0], a6[0]), name='af', dur=a6[1])
        bp.insertSegment(7, ramp, (a6[0], a7[0]), name='ag', dur=a7[1])
        bp.insertSegment(8, ramp, (readout[0], readout[0]), name='readout', dur=readout[1])
        bp.insertSegment(9, ramp, (readout[0], a8[0]), name='ah', dur=a8[1])
        bp.insertSegment(10, ramp, (a8[0], a9[0]), name='ai', dur=a9[1])

        return bp

    def spin_dephasing_blue_print(self, a1, eta,
                                  readout, a8, a9):
        bp = bb.BluePrint()
        bp.insertSegment(0, ramp, (a1[0], a1[0]), name='aa', dur=a1[1])
        bp.insertSegment(1, ramp, (eta[0], eta[0]), name='eta', dur=eta[1])
        bp.insertSegment(2, ramp, (readout[0], readout[0]), name='readout', dur=readout[1])
        bp.insertSegment(3, ramp, (readout[0], a8[0]), name='ah', dur=a8[1])
        bp.insertSegment(4, ramp, (a8[0], a9[0]), name='ai', dur=a9[1])

        return bp

    def bp_int_to_zero(self, bp):
        num_seg = self.number_of_segments(bp)
        tottime = 0
        tottimevolt = 0
        for i in range(num_seg):
            pulsestart = bp.description[f'segment_{i+1:02d}']['arguments']['start']
            pulsestop = bp.description[f'segment_{i+1:02d}']['arguments']['stop']
            pulsedur = bp.description[f'segment_{i+1:02d}']['durations']
            tottime += pulsedur
            tottimevolt += pulsedur*(pulsestart+pulsestop)/2
        timeD = tottime/1.65
        voltD = -tottimevolt/timeD

        bp.insertSegment(num_seg, ramp, (voltD, voltD),
                         name='CorretD', dur=timeD)
        return bp

    def number_of_segments(self, bp):
        nr = len(bp.description)-4
        return nr

    def update_seq_from_list(self, x, y, ramp):
        self.update_df_from_list(x, y, ramp)
        self.seq_from_df()

    def df_from_list(self, x, y, ramp):
        dim = len(x)
        names = list(string.ascii_lowercase)[:dim]
        times = [1]*dim
        bbtype = ['ramp']*dim
        chaninit = [0]*dim
        markerinit = [False]*dim
        index = list(range(1, dim+1, 1))
        self.df = pd.DataFrame({
                                'name': names,
                                'time': times,
                                'type': bbtype,
                                f'ch{self.ch_x}': chaninit,
                                f'ch{self.ch_y}': chaninit,
                                f'm{self.ch_x}1': markerinit,
                                f'm{self.ch_y}1': markerinit,
                                f'm{self.ch_x}2': markerinit,
                                f'm{self.ch_y}2': markerinit
                               }, index=index
                               )
        self.update_df_from_list(x, y, ramp)

    def update_df_from_list(self, x, y, ramp):
        x = np.array(x)-self.zero_point[0]
        y = np.array(y)-self.zero_point[1]
        rec_info_x = self.get_recurcive_info(f'ch{self.ch_x}')
        rec_info_y = self.get_recurcive_info(f'ch{self.ch_y}')
        for i in range(len(x)):
            if ramp[i] and i != 0:
                self.df.loc[i+1, f'ch{self.ch_x}'] = f'{x[i-1]/self.scale:.2f}, {x[i]/self.scale:.2f}'
                self.df.loc[i+1, f'ch{self.ch_y}'] = f'{y[i-1]/self.scale:.2f}, {y[i]/self.scale:.2f}'
            else:
                if rec_info_x[i]:
                    a = x[i]/self.scale
                    b = x[i]/self.scale+rec_info_x[1]-rec_info_x[0]
                    nr = rec_info_x[i][1]
                    self.df.loc[i+1, f'ch{self.ch_x}'] = f'{a:.2f},{b:.2f},{nr}'
                else:
                    self.df.loc[i+1, f'ch{self.ch_x}'] = f'{x[i]/self.scale:.2f}'
                if rec_info_y[i]:
                    a = y[i]/self.scale
                    b = y[i]/self.scale+rec_info_y[1]-rec_info_y[0]
                    nr = rec_info_y[i][1]
                    self.df.loc[i+1, f'ch{self.ch_y}'] = f'{a:.2f},{b:.2f},{nr}'
                else:
                    self.df.loc[i+1, f'ch{self.ch_y}'] = f'{y[i]/self.scale:.2f}'

    def get_recurcive_info(self, ch):
        # should this function be moved to dfsequence
        return [self.find_recurcive_info(x) for x in self.df[ch].values]

    def find_recurcive_info(self, x):
        if type(x) in [list, str] and len(list_or_sting(x)) == 3:
            rec_list = list_or_sting(x)
            return rec_list
        else:
            return 0


class AWGController(SpinBuilder):
    def __init__(self, name: str, awg=None, **kwargs):
        super().__init__(name, **kwargs)
        self.awg = awg

    def uploadToAWG(self, awg_amp: list = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]) -> None:
        if '5014' in str(self.awg.__class__):
            # for i,  chan in enumerate(self.seq.get().channels):
            #    self.awg.channels[chan].AMP(float(chbox[chan-1].text()))
            self.awg.ch1_amp(4.5)
            self.awg.ch2_amp(4.5)
            self.awg.ch3_amp(4.5)
            self.awg.ch4_amp(4.5)
            package = self.seq.get().outputForAWGFile()
            start_time = time.time()
            self.awg.make_send_and_load_awg_file(*package[:])
            print("Sequence uploaded in %s seconds" % (time.time()-start_time))
        elif '5208' in str(self.awg.__class__):
            self.seq.get().name = 'sequence_from_gui'
            self.awg.mode('AWG')
            for chan in self.seq.get().channels:
                self.awg.channels[chan-1].resolution(12)
                self.awg.channels[chan-1].awg_amplitude(awg_amp[chan-1])
                self.seq.get().setChannelAmplitude(chan, self.awg.channels[chan-1].awg_amplitude())
            self.awg.clearSequenceList()
            self.awg.clearWaveformList()
            self.awg.sample_rate(self.seq.get().SR)
            self.awg.sample_rate(self.seq.get().SR)

            seqx_input = self.seq.get().outputForSEQXFile()
            start_time = time.time()
            seqx_output = self.awg.makeSEQXFile(*seqx_input)
            # transfer it to the awg harddrive
            self.awg.sendSEQXFile(seqx_output, 'sequence_from_gui.seqx')
            self.awg.loadSEQXFile('sequence_from_gui.seqx')
            # time.sleep(1.300)
            for i,  chan in enumerate(self.seq.get().channels):
                self.awg.channels[chan-1].setSequenceTrack('sequence_from_gui', i+1)
                self.awg.channels[chan-1].state(1)
            print("Sequence uploaded in %s seconds" % (time.time()-start_time))

        else:
            print('Choose an AWG model')

    def runAWG(self):
        if '5014' in str(self.awg.__class__):
            self.awg.run()
        else:
            seq_chan = self.seq.get().channels
            for i, chan in enumerate(self.awg.channels):
                if i+1 in seq_chan:
                    chan.state(1)
                else:
                    chan.state(0)
            self.awg.play()

    def seq_settings_infinity_loop(self, elem_nr: int, last_elem_nr: int) -> None:
        """
        Play element 1 time and go to the next,
        except if you are the last element, then play 1 time and go to the first Element.

        args:
        elem_nr (int): the number of the element
        last_elem_nr (int): the number of the last element in the sequence
        """
        self.seq.seq.setSequencingTriggerWait(elem_nr, 0)
        self.seq.seq.setSequencingNumberOfRepetitions(elem_nr, 1)
        self.seq.seq.setSequencingEventJumpTarget(elem_nr, 0)
        if elem_nr == last_elem_nr:
            self.seq.seq.setSequencingGoto(elem_nr, 1)
        else:
            self.seq.seq.setSequencingGoto(elem_nr, 0)


class AlazarAWG(AWGController):
    def __init__(self, name: str, awg=None,
                 alazar=None,
                 alazar_ctrl=None,
                 alazar_channel=None,
                 **kwargs):
        super().__init__(name, awg, **kwargs)
        self.alazar = alazar
        self.alazar_ctrl = alazar_ctrl
        self.alazar_channel = alazar_channel
