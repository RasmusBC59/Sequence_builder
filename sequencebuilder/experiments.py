
from qcodes.utils.dataset.doNd import do0d
from sequencebuilder.awg_controller import AWGController


class TransmonExperiment(AWGController):
    def __init__(self,name:str, awg=None, alazar_ctrl,**kwargs):
        super().__init__(name, awg, **kwargs)
        self.alazar_ctrl = alazar_ctrl
        self.npts=None


    def experimet_one(self):

        USE_DEMOD_FREQ = 20e6
        alazar_ctrl.channels[0].demod_freq(USE_DEMOD_FREQ)
        alazar_ctrl.channels[1].demod_freq(USE_DEMOD_FREQ)
        alazar_ctrl.int_time(0.6e-6)
        alazar_ctrl.int_delay(0E-9)
        setpoint = SC.seqbuild.x_val()
        num_averages = 80
        for ala_chan in alazar_ctrl.channels[:]:
            ala_chan.demod_freq(USE_DEMOD_FREQ)
            ala_chan.num_averages(num_averages)
            ala_chan.records_per_buffer(npts)
            ala_chan.data.setpoint_labels = ('SSB Drive frequency (Non-overlap)',)
            ala_chan.data.setpoint_units = ('Hz',)
            ala_chan.prepare_channel()
            ala_chan.data.setpoints = (tuple(setpoint),)    


    def MultiQ_SSB_Spec_NoOverlap(self, start:float, stop:float, npts:int):
        seqbuild.cycle_time = 4e-6
        seqbuild.pulse_time = 0.6e-6
        seqbuild.readout_time = 1.5e-6
        seqbuild.marker_offset = 0e-9
        seqbuild.SR.set(1.5e9)
        seqbuild.readout_freq_1(6.6104e9)
        seqbuild.MultiQ_SSB_Spec_NoOverlap(start, stop, npts)
        seqbuild.uploadToAWG()
        seqbuild.runAWG()

        #prepare switches and instruments

        switch.a(2)
        switch.b(2)

        #Turn Rohde and Schwarz boxes on and allow IQ modulation
        cavity.status(1)  
        cavity.IQ_state(1)
        qubit.status(1)
        qubit.IQ_state(1)


        # set cavity and qubit power manually
        USE_READOUT_FREQ = 6609095000
        USE_DEMOD_FREQ = 20e6
        USE_READOUT_POWER = -15
        cavity.power(USE_READOUT_POWER)
        qubit.power(-40)

        cavity.frequency(USE_READOUT_FREQ - USE_DEMOD_FREQ) 
        alazar_ctrl.channels.append(rec_f1_mag)
        alazar_ctrl.channels.append(rec_f1_phase)
        alazar_ctrl.channels[0].demod_freq(USE_DEMOD_FREQ)
        alazar_ctrl.channels[1].demod_freq(USE_DEMOD_FREQ)
        for n, ala_chan in enumerate(alazar_ctrl.channels[0:2]):
            ala_chan.records_per_buffer(npts)
            ala_chan.data.setpoint_labels = ('SSB Drive frequency (Non-overlap)',)
            ala_chan.data.setpoint_units = ('Hz',)
        alazar_ctrl.int_delay(2e-7)
        alazar_ctrl.int_time(0.5e-6)
        rec_f1_phase.records_per_buffer(npts)
        rec_f1_phase.num_averages(80)
        data1 = do0d(rec_f1_phase.data)
        