# Created By: Virgil Dupras
# Created On: 2008-09-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .. import aiff
from .util import TestData, eq_

def test_random():
    # a random file is not valid but has its attributes set.
    f = aiff.File(TestData.filepath('randomfile'))
    assert not f.valid
    eq_(f.duration, 0)
    eq_(f.sample_rate, 0)
    eq_(f.bitrate, 0)
    assert f.tag is None
    eq_(f.audio_offset, 0)
    eq_(f.audio_size, 0)

def test_long_comm_field():
    # some COMM fields are longer than 18 bytes. They must be supported
    f = aiff.File(TestData.filepath('aiff/long_comm_field.aif'))
    assert f.valid
    eq_(f.duration, 132)

def test_with_id3():
    # this file is a track encoded from a CD with iTunes. It has a ID3 chunk. The SSND chunk
    # has been manually truncated (the file was 22mb)
    f = aiff.File(TestData.filepath('aiff/with_id3.aif'))
    assert f.valid
    eq_(f.duration, 132)
    eq_(f.sample_rate, 44100)
    eq_(f.bitrate, 1411200)
    eq_(f.tag.artist, 'Assimil') # The id3v2 module takes care of it, no need to test it further
    eq_(f.audio_offset, 46)
    eq_(f.audio_size, 42)

