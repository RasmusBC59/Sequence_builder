import broadbean as bb
from qcodes import validators as vals
from sequencebuilder.back_of_beans import BagOfBeans
import time
ramp = bb.PulseAtoms.ramp



class AWGController(SpinBuilder):
    def __init__(self, name: str, awg=None, **kwargs):
        super().__init__(name, **kwargs)
        self.awg = awg        
    def uploadToAWG(self, awg_amp: list = [0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5]) -> None:
        if '5014' in str(self.awg.__class__):
            #for i,  chan in enumerate(self.seq.get().channels):
            #    self.awg.channels[chan].AMP(float(chbox[chan-1].text()))
            self.awg.ch1_amp(awg_amp[0])
            self.awg.ch2_amp(awg_amp[1])
            self.awg.ch3_amp(awg_amp[2])
            self.awg.ch4_amp(awg_amp[3])
            package = self.seq.get().outputForAWGFile()
            start_time = time.time()
            self.awg.make_send_and_load_awg_file(*package[:])
            print("Sequence uploaded in %s seconds" %(time.time()-start_time));
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
            start_time=time.time()
            seqx_output = self.awg.makeSEQXFile(*seqx_input)
            # transfer it to the awg harddrive
            self.awg.sendSEQXFile(seqx_output, 'sequence_from_gui.seqx')
            self.awg.loadSEQXFile('sequence_from_gui.seqx')
            #time.sleep(1.300)
            for i,  chan in enumerate(self.seq.get().channels):       
                self.awg.channels[chan-1].setSequenceTrack('sequence_from_gui', i+1)
                self.awg.channels[chan-1].state(1)
            print("Sequence uploaded in %s seconds" %(time.time()-start_time))
 
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

class SpinBuilder(BagOfBeans):

    def __init__(self,name:str, **kwargs):
        super().__init__(name, **kwargs)

    def spin_funnel_seq(self, a1, a2, a3, eta, readout, a5, a6):

        self.seq = bb.Sequence()
        for i, _ in enumerate(eta[0]):
            elem = bb.Element()
            bp = spin_funnel_blue_print((a1[0], a1[2]), (a2[0], a2[2]), (a3[0], a3[2]),
                                        (eta[0][i], eta[2]), (readout[0],readout[2]), (a5[0], a5[2]), (a6[0], a6[2]))
            bp.setSegmentMarker('readout', (0.0, 0.5e-6), 1)
            bp = bp_int_to_zero(bp)
            if i == 0:
                bp.setSegmentMarker('aa', (0.0, 0.5e-6), 2)
            bp2 = spin_funnel_blue_print((a1[1], a1[2]), (a2[1], a2[2]), (a3[1], a3[2]),
                                         (eta[1][i], eta[2]), (readout[1], readout[2]), (a5[1], a5[2]), (a6[1], a6[2]))
            bp2 = bp_int_to_zero(bp2)
            bp.setSR(1e7)
            bp2.setSR(1e7)
            elem.addBluePrint(1, bp)
            elem.addBluePrint(2, bp2)
            #elem = elem_int_to_zero(elem)
            self.seq.addElement(i+1, elem)
            self.seq.setSR(1e7)

    def spin_funnel_blue_print(a1, a2, a3, eta, readout, a5, a6):
        bp = bb.BluePrint()
        bp.insertSegment(0, ramp, (a1[0], a1[0]), name='aa', dur=a1[1])
        bp.insertSegment(1, ramp, (a1[0], a2[0]), name='ab', dur=a2[1])
        bp.insertSegment(2, ramp, (a3[0], a3[0]), name='ac', dur=a3[1])
        bp.insertSegment(3, ramp, (eta[0], eta[0]), name='eta', dur=eta[1])
        bp.insertSegment(4, ramp, (readout[0], readout[0]), name='readout', dur=readout[1])
        bp.insertSegment(5, ramp, (readout[0], a5[0]), name='ad', dur=a5[1])
        bp.insertSegment(6, ramp, (a6[0], a6[0]), name='ae', dur=a6[1])
        return bp

    def elem_int_to_zero(elem):
        channels = elem.channels
        num_chan = len(elem.channels)
        for j in range(num_chan):
            num_seg = number_of_segments(elem,j)
            tottime = 0
            tottimevolt = 0
            for i in range(num_seg):
                pulsestart = elem.description['{}'.format(j+1)]['segment_%02d'%(i+1)]['arguments']['start']
                pulsestop = elem.description['{}'.format(j+1)]['segment_%02d'%(i+1)]['arguments']['stop']
                pulsedur = elem.description['{}'.format(j+1)]['segment_%02d'%(i+1)]['durations']
                tottime += pulsedur
                print(tottime)
                tottimevolt += pulsedur*(pulsestart+pulsestop)/2
            timeD = tottime/1.65
            voltD = -tottimevolt/timeD
            bp = bb.BluePrint()
            print('hep')
            bp.insertSegment(num_seg, ramp, (voltD, voltD),
                            name='CorretD', dur=timeD)
            bp.setSR(1e7)
            elem.addBluePrint(channels[j], bp)
        return elem

    def _number_of_segments(elem,j):
        nr = len(elem.description['{}'.format(elem.channels[j])])-4
        return nr

    def bp_int_to_zero(bp):
        num_seg = number_of_segments(bp)
        tottime = 0
        tottimevolt = 0
        for i in range(num_seg):
            pulsestart = bp.description['segment_%02d'%(i+1)]['arguments']['start']
            pulsestop = bp.description['segment_%02d'%(i+1)]['arguments']['stop']
            pulsedur = bp.description['segment_%02d'%(i+1)]['durations']
            tottime += pulsedur
            print(tottime)
            tottimevolt += pulsedur*(pulsestart+pulsestop)/2
        timeD = tottime/1.65
        voltD = -tottimevolt/timeD

 
        bp.insertSegment(num_seg, ramp, (voltD, voltD),
                            name='CorretD', dur=timeD)
        return bp

    def number_of_segments(bp):
        nr = len(bp.description)-4
        return nr
