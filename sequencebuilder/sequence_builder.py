import numpy as np
import broadbean as bb
from qcodes import validators as vals
from sequencebuilder.back_of_beans import BagOfBeans



ramp = bb.PulseAtoms.ramp  # args: start, stop
sine = bb.PulseAtoms.sine  # args: freq, ampl, off, phase
gausian =  bb.PulseAtoms.gaussian_smooth_cutoff # args: ampl, sigma, mu, offset

class SequenceBuilder(BagOfBeans):
    """
    Class for generating Sequences with predefined patterns

        Attributes
        ----------
        cycle_time : float
            total time of each cycle 
        pulse_time : float
            duration of the pulse
        readout_time : float
            duration of the readout
        marker_offset : float
            releative offset with respect to the readout_time
        SR: float
            sampling rate 

        Methods
        -------
        MultiQ_SSB_Spec_NoOverlap
            sequence of two channels with orthogonal sine/cosine pulses and two channels for the readout
        MultiQ_Lifetime_overlap
            One channels containing a pi-pulse
            varying the time between the end of the pi-pulse and the readout and two channels for the readout
    """

    def __init__(self,name:str,number_read_freqs:int = 1,**kwargs):
        super().__init__(name, **kwargs)

        self.add_parameter('cycle_time',
                      label='Pulse Cycle Time',
                      unit='s',
                      set_cmd= lambda x : x,
                      vals=vals.Numbers(0,10e-3))
        self.add_parameter('pulse_time',
                      label='Pulse Time',
                      unit='s',
                      set_cmd= lambda x : x,
                      vals=vals.Numbers(0,10e-3))                      
        self.add_parameter('readout_time',
                      label='Readout Duration',
                      unit='s',
                      set_cmd= lambda x : x,
                      vals=vals.Numbers(0,0.2e-3))
        self.add_parameter('marker_offset',
                      label='Marker Offset',
                      unit='s',
                      set_cmd= lambda x : x,
                      vals=vals.Numbers(-1e-5,1e-5))
        for i in range(number_read_freqs):
            self.add_parameter('readout_freq_{}'.format(i+1),
                        label='Readout Frequency {}'.format(i+1),
                        unit='Hz',
                        set_cmd= lambda x : x,
                        vals=vals.Numbers(0,12.5e9))
        self.add_parameter(x_val,
                            label=''
                            unit=''
                            )

    def MultiQ_SSB_Spec_NoOverlap(self, start:float, stop:float, npts:int) -> None:
        """ 
        Updates the broadbean sequence so it contains two channels with orthogonal sine/cosine pulses for an array of  frequencies
        and two channels for the readout for IQ mixing 

            args:
            start (float): Starting point of the frequency interval
            stop (float): Endpoint point of the frequency interval
            npts (int): Number of point in the frequency interval
        """
        self.seq.empty_sequence()
        freq_interval = np.linspace(start,stop,npts)
        readout_freq = self.readout_freq_1.get() #- self.cavity.frequency()
        self.x_val = freq_interval
        for i,f in enumerate(freq_interval):
            self.elem = bb.Element()
            if i == 0:
                seg_sin = self.seg_sine(frequency = f,marker=True)
            else:
                seg_sin = self.seg_sine(frequency = f, marker=False)
            seg_cos = self.seg_sine(frequency = f, phase=np.pi/2)
            self.elem.addBluePrint(1, seg_sin)
            self.elem.addBluePrint(2, seg_cos)
            self.elem_add_readout_pulse(readout_freq)
            self.seq.seq.addElement(i+1, self.elem)
            self.seq_settings_infinity_loop(i+1,npts)
        self.seq.seq.setSR(self.SR.get())

        self.seq.set_all_channel_amplitude_offset(amplitude=1, offset=0)
   

    def MultiQ_Lifetime_overlap_variation(self, start:float, stop:float, npts:int) -> None:
        """ 
        Updates the broadbean sequence so it contains one channels containing a pi-pulse
        varying the time between the end of the pi-pulse and the readout
        and two channels for the readout for IQ mixing 
        
            args:
            start (float): Starting point of the delta time
            stop (float): Endpoint point of the delta time
            npts (int): Number of point in the time interval
        """
        
        self.seq.empty_sequence()
        readout_freq = self.readout_freq_1.get()
        pulse_to_readout_time = np.linspace(start,stop,npts)
        readout_freq = self.readout_freq_1.get() #- self.cavity.frequency()
        for i,delta_time in enumerate(pulse_to_readout_time):
            self.elem = bb.Element()
            if i == 0:
                seg_pi = self.seg_pi_overlap(pulse_time=self.pulse_time, overlap_time = delta_time , marker=True)
            else:
                seg_pi = self.seg_pi_overlap(pulse_time=self.pulse_time, overlap_time = delta_time, marker=False)
            self.elem.addBluePrint(1, seg_pi)
            self.elem_add_readout_pulse(readout_freq)
            self.seq.seq.addElement(i+1,self.elem)

            self.seq_settings_infinity_loop(i+1,npts)
        self.seq.seq.setSR(self.SR.get())
      
        self.seq.set_all_channel_amplitude_offset(amplitude=1, offset=0)

    def MultiQ_Lifetime_overlap(self, start:float, stop:float, npts:int, overlap_time:float) -> None:
        """ 
        Updates the broadbean sequence so it contains one channels containing a pi-pulse
        varying the time between the end of the pi-pulse and the readout
        and two channels for the readout for IQ mixing 
        
            args:
            start (float): Starting point of the delta time
            stop (float): Endpoint point of the delta time
            npts (int): Number of point in the time interval
        """
        
        self.seq.empty_sequence()
        readout_freq = self.readout_freq_1.get()
        pulse_to_readout_time = np.linspace(start,stop,npts)
        readout_freq = self.readout_freq_1.get() #- self.cavity.frequency()
        for i,delta_time in enumerate(pulse_to_readout_time):
            self.elem = bb.Element()
            if i == 0:
                seg_pi = self.seg_pi_overlap(delta_time, overlap_time, marker=True)
            else:
                seg_pi = self.seg_pi_overlap(delta_time, overlap_time, marker=False)
            self.elem.addBluePrint(1, seg_pi)
            self.elem_add_readout_pulse(readout_freq)
            self.seq.seq.addElement(i+1,self.elem)

            self.seq_settings_infinity_loop(i+1,npts)
        self.seq.seq.setSR(self.SR.get())
      
        self.seq.set_all_channel_amplitude_offset(amplitude=1, offset=0)
   

    def give_me_a_name(self, start:float, stop:float, npts:int) -> None:
        """ 
        Updates the broadbean sequence so it contains one channels containing a gausian
        varying sigma
        and two channels for the readout for IQ mixing 
        
            args:
            start (float): Starting point of the sigma interval
            stop (float): Endpoint point of the sigma interval
            npts (int): Number of point in the sigma interval
        """
        
        self.seq.empty_sequence()
        readout_freq = self.readout_freq_1.get()
        sigma_interval = np.linspace(start,stop,npts)
        readout_freq = self.readout_freq_1.get() #- self.cavity.frequency()
        for i,sigma in enumerate(sigma_interval):
            self.elem = bb.Element()
            if i == 0:
                seg_g = self.seg_gausian(sigma=sigma, marker=True)
            else:
                seg_g = self.seg_gausian(sigma=sigma, marker=False)
            self.elem.addBluePrint(1, seg_g)
            self.elem_add_readout_pulse(readout_freq)
            self.seq.seq.addElement(i+1,self.elem)

            self.seq_settings_infinity_loop(i+1,npts)
        self.seq.seq.setSR(self.SR.get())
      
        self.seq.set_all_channel_amplitude_offset(amplitude=1, offset=0)        
        

    def seg_sine(self,
                frequency:float,
                phase:float = 0,
                marker:bool = False) -> bb.BluePrint:
        """
        Returns a broadbean BluePrint contaning a flat segment, sine segment and a flat segment for readout

        args:
        frequency (float): frequency of the sine 
        phase (float): phase of the sine
        marker (bool): include marker 
        """
        
        first_time = self.cycle_time-self.pulse_time-self.readout_time 
        
        seg_sin = bb.BluePrint()
        seg_sin.insertSegment(0, ramp, (0, 0), name='first', dur=first_time)
        seg_sin.insertSegment(1, sine, (frequency, 1e-3, 0, phase), name='pulse', dur=self.pulse_time)
        seg_sin.insertSegment(2, ramp, (0, 0), name='read', dur=self.readout_time)
        if marker:
            seg_sin.marker1 = [(first_time+self.pulse_time+self.marker_offset, self.cycle_time)]
        seg_sin.setSR(self.SR.get())
        
        return seg_sin

    def seg_pi_overlap(self,
                       pulse_time:float = 0, overlap_time:float = 0,marker:bool = False) -> bb.BluePrint:
        """
        Returns a broadbean BluePrint of a PI pulse 

        args:
        pulse_to_readout_time (float): time between the end of the PI pulse and the readout  
        """
        
        first_time = self.cycle_time-pulse_time-self.readout_time + overlap_time
        end_time = self.cycle_time -first_time - pulse_time 
        
        seg_sin = bb.BluePrint()
        if pulse_time < 2/self.SR.get():
            seg_sin.insertSegment(0, ramp, (0, 0), name='first', dur=(first_time+pulse_time)/2.0)
            seg_sin.insertSegment(1, ramp, (0.0, 0.0), name='pulse', dur=(first_time+pulse_time)/2.0)
            seg_sin.insertSegment(2, ramp, (0, 0), name='read', dur=end_time)
        else:
            seg_sin.insertSegment(0, ramp, (0, 0), name='first', dur=first_time)
            seg_sin.insertSegment(1, ramp, (0.25, 0.25), name='pulse', dur=pulse_time)
            seg_sin.insertSegment(2, ramp, (0, 0), name='read', dur=end_time)
        if marker:
            seg_sin.marker1 = [(first_time+pulse_time+self.marker_offset, self.cycle_time)]
        seg_sin.setSR(self.SR.get())
        
        return seg_sin        
    


    def seg_gausian(self,
                    pulse_to_readout_time:float = 0,
                    ampl:float = 1,
                    sigma:float = 1e-9,
                    mu:float = 0,
                    offset: float = 0,
                    marker:bool = False
                    ) -> bb.BluePrint:
        """
        Returns a broadbean BluePrint of a gausian pulse 

        args:
        pulse_to_readout_time (float): time between the end of the gausion pulse and the readout
        marker (bool): include marker 
        """
        time_sigma = 5*sigma
        first_time = self.cycle_time-time_sigma-self.readout_time-pulse_to_readout_time 
        end_time = self.readout_time+pulse_to_readout_time
        
        seg_g = bb.BluePrint()
        seg_g.insertSegment(0, ramp, (0, 0), name='first', dur=first_time)
        seg_g.insertSegment(1, gausian, (ampl, sigma,mu,offset), name='pulse', dur=time_sigma)
        seg_g.insertSegment(2, ramp, (0, 0), name='read', dur=end_time)
        if marker:
            seg_g.marker1 = [(first_time+time_sigma+self.marker_offset+pulse_to_readout_time, self.cycle_time)]
        seg_g.setSR(self.SR.get())
        
        return seg_g      




    def seq_settings_infinity_loop(self, elem_nr:int, last_elem_nr:int) -> None:
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


    def elem_add_readout_pulse(self, frequency:float, amplitude:float = 0.05):
        seg_sin_readout = self.seg_sine_readout(frequency=frequency, amplitude=amplitude, marker=False)
        seg_cos_readout = self.seg_sine_readout(frequency=frequency, amplitude=amplitude, phase=np.pi/2 ,marker=True)
        self.elem.addBluePrint(3,seg_sin_readout)
        self.elem.addBluePrint(4,seg_cos_readout)


    def seg_sine_readout(self,
                frequency:float,
                phase:float = 0,
                amplitude:float = 1e-3,
                marker:bool = True ) -> bb.BluePrint:
        """
        Returns a broadbean BluePrint contaning a flat segment, sine segment and a flat segment for readout

        args:
        frequency (float): frequency of the sine 
        phase (float): phase of the sine 
        """
        
        first_time = self.cycle_time-self.readout_time 
        
        seg_sin = bb.BluePrint()
        seg_sin.insertSegment(0, ramp, (0, 0), name='first', dur=first_time)
        seg_sin.insertSegment(1, sine, (frequency, amplitude, 0, phase), name='pulse', dur=self.readout_time)
        if marker:
            seg_sin.marker1 = [(first_time+self.marker_offset, self.cycle_time)]
        seg_sin.setSR(self.SR.get())
        
        return seg_sin

