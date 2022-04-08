import pytest
import broadbean as bb
from sequencebuilder.back_of_beans import ParSeq, BagOfBeans


@pytest.fixture
def seq_fixture():
    ramp = bb.PulseAtoms.ramp  # args: start, stop
    sine = bb.PulseAtoms.sine  # args: freq, ampl, off, phase
    seq1 = bb.Sequence()
    bp_square = bb.BluePrint()
    bp_square.setSR(1e9)
    bp_square.insertSegment(0, ramp, (0, 0), dur=100e-9)
    bp_square.insertSegment(1, ramp, (1e-3, 1e-3), name='top', dur=100e-9)
    bp_square.insertSegment(2, ramp, (0, 0), dur=100e-9)
    bp_boxes = bp_square + bp_square

    bp_sine = bb.BluePrint()
    bp_sine.setSR(1e9)
    bp_sine.insertSegment(0, sine, (3.333e6, 1.5e-3, 0, 0), dur=300e-9)
    bp_sineandboxes = bp_sine + bp_square
    bp_sineandboxes.setSegmentMarker('ramp', (-0.0, 100e-9), 1)
    bp_sineandboxes.setSegmentMarker('sine', (-0.0, 100e-9), 2)
    elem1 = bb.Element()
    elem1.addBluePrint(1, bp_boxes)
    elem1.addBluePrint(3, bp_sineandboxes)

    elem2 = bb.Element()
    elem2.addBluePrint(3, bp_boxes)
    elem2.addBluePrint(1, bp_sineandboxes)

    seq1.addElement(1, elem1)
    seq1.addElement(2, elem2)
    seq1.addElement(3, elem1)
    seq1.setSR(1e9)
    return seq1


@pytest.fixture()
def parseq_fixture(seq_fixture):
    parseq = ParSeq(name='parseq')
    parseq.set(seq_fixture)
    return parseq


@pytest.fixture()
def back_of_beans(seq_fixture):
    back_of_beans = BagOfBeans()
    back_of_beans.

def test_get(seq_fixture):
    parseq = ParSeq(name='parseq')
    parseq.set(seq_fixture)

    assert parseq.get() == seq_fixture


def test_empty_sequence(parseq_fixture):
    SR = parseq_fixture.seq.SR
    parseq_fixture.empty_sequence()
    description_dict = {'awgspecs': {'SR': SR}}
    assert parseq_fixture.seq.description == description_dict


def test_set_all_channel_amplitude_offset(parseq_fixture):
    amplitude = 1.2
    offset = 0.3
    parseq_fixture.set_all_channel_amplitude_offset(amplitude=amplitude, offset=offset)
    awgspecs = parseq_fixture.seq.description['awgspecs']
    for ch in parseq_fixture.seq.channels:
        assert awgspecs[f'channel{ch}_amplitude'] == amplitude
        assert awgspecs[f'channel{ch}_offset'] == offset


def test_number_of_elements(parseq_fixture):
    assert parseq_fixture.number_of_elements() == 3


def test_seq_settings_infinity_loop(parseq_fixture):
    parseq_fixture.seq_settings_infinity_loop()
    description = parseq_fixture.seq.description
    list_of_elements = list(description.keys())[:-1]
    for seq_nr in list_of_elements[:-1]:
        dict_sequencing = description[seq_nr]['sequencing']
        assert dict_sequencing == {'Wait trigger': 0,
                                   'Repeat': 1,
                                   'jump_input': 0,
                                   'jump_target': 0,
                                   'Go to': 0}
    seq_nr = list_of_elements[-1]
    dict_sequencing = description[seq_nr]['sequencing']
    assert dict_sequencing == {'Wait trigger': 0,
                               'Repeat': 1,
                               'jump_input': 0,
                               'jump_target': 0,
                               'Go to': 1}


def test_plot(parseq_fixture):
    parseq_fixture.plot()


def test_plot_elem_nr(parseq_fixture):
    parseq_fixture.plot_elem_nr(1)

def test_to_file():
    pass


def test_from_file():
    pass

def test_set_sample_rate():
    pass


def test_get_sample_rate():
    pass
