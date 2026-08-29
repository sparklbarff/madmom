"""
Pins the tuple-subclass handling in TCNTempoHistogramProcessor.process().

The method used `type(data) == tuple`, which is exact-type and therefore false for
every tuple SUBCLASS. A namedtuple carrying multi-task TCN output would fall
through the branch and be treated as the tempo array itself, so the processor
would slice the whole multi-task output as if it were a histogram and return
numbers rather than raise. That is the failure direction that does not announce
itself.

The discriminating pair is the point here: the plain-tuple case passed before the
fix and still passes, so on its own it proves nothing. The namedtuple case is the
one that distinguishes `isinstance` from `==`.
"""

from collections import namedtuple

import numpy as np

from madmom.features.tempo import TCNTempoHistogramProcessor

# Wide enough to survive the min_bpm/max_bpm slice with room to spare.
ACTIVATIONS = np.linspace(0.0, 1.0, 300)
MultiTask = namedtuple("MultiTask", ["beats", "downbeats", "tempo"])


def _process(data):
    return TCNTempoHistogramProcessor().process(data)


def test_a_plain_tuple_takes_the_last_item():
    """The case that already worked. Included as the control, not as the evidence."""
    bins, tempi = _process((np.zeros(300), ACTIVATIONS))
    assert len(bins) == len(tempi)
    assert bins.max() > 0, "the last item was selected, not the zeros"


def test_a_namedtuple_also_takes_the_last_item():
    """The case `type(data) == tuple` got wrong.

    Before the fix this did not raise; it silently treated the 3-element namedtuple
    as the activation array, which is why nothing caught it.
    """
    bins, tempi = _process(MultiTask(np.zeros(300), np.zeros(300), ACTIVATIONS))
    assert len(bins) == len(tempi)
    assert bins.max() > 0, "the tempo field was selected, not a zeroed task"


def test_a_bare_array_is_passed_through_untouched():
    """A non-tuple must NOT be unpacked. Guards against 'fix' by always indexing."""
    bins, tempi = _process(ACTIVATIONS)
    assert len(bins) == len(tempi)
    assert bins.max() > 0


def test_the_namedtuple_and_plain_tuple_agree():
    """Same tempo payload in both shapes must give byte-identical output.

    This is what makes the namedtuple test evidence rather than a smoke test: it
    fails if the subclass takes any different path at all.
    """
    plain_bins, plain_tempi = _process((np.zeros(300), np.zeros(300), ACTIVATIONS))
    named_bins, named_tempi = _process(MultiTask(np.zeros(300), np.zeros(300), ACTIVATIONS))
    np.testing.assert_array_equal(plain_bins, named_bins)
    np.testing.assert_array_equal(plain_tempi, named_tempi)
