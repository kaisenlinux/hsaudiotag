# Created By: Virgil Dupras
# Created On: 2005/02/06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .. import wma
from .util import TestData, eq_

def test1():
    # test1.wma is a normal, valid wma file
    w = wma.WMADecoder(TestData.filepath('wma/test1.wma'))
    eq_(w.artist, 'Modest Mouse')
    eq_(w.album, 'The Moon & Antarctica')
    eq_(w.title, '3rd Planet')
    eq_(w.genre, 'Rock')
    eq_(w.comment, '')
    eq_(w.year, '2000')
    eq_(w.track, 1)
    eq_(w.bitrate, 192)
    eq_(w.size, 77051)
    eq_(w.duration, 239)
    eq_(w.audio_offset, 0x15a0)
    eq_(w.audio_size, 0x582682 - 0x15a0)
    assert w.valid

def test2():
    # test2.wma is a mpeg file, thus invalid
    w = wma.WMADecoder(TestData.filepath('wma/test2.wma'))
    assert not w.valid
    eq_(w.audio_offset, 0)
    eq_(w.audio_size, 0)

def testZeroFile():
    w = wma.WMADecoder(TestData.filepath('zerofile'))
    assert not w.valid

def test1_non_ascii():
    # The album is Unicode
    w = wma.WMADecoder(TestData.filepath('wma/test1_non_ascii.wma'))
    assert isinstance(w.album, str)
    eq_(w.album, 'The Moon \u00c8 Antarctica')

def test1_no_track():
    # This is a file with no WM/TRACK field
    w = wma.WMADecoder(TestData.filepath('wma/test1_no_track.wma'))
    eq_(0, w.track)
    
def test3():
    # This is the file that made a customer's musicGuru copy bug. It was because it has no track.
    w = wma.WMADecoder(TestData.filepath('wma/test3.wma'))
    eq_(w.artist, 'Giovanni Marradi')
    eq_(w.album, 'Always')
    eq_(w.title, 'Gideon')
    eq_(w.genre, 'Easy Listening')
    eq_(w.comment, '')
    eq_(w.year, '')
    eq_(w.track, 0)
    eq_(w.bitrate, 48)
    eq_(w.size, 80767)
    eq_(w.duration, 238)
    assert w.valid

def test3_truncated_unicode():
    # This is the file has its WM/GENRE field last char truncated. Its value, 'Easy Listening' 
    # also has one char truncated. 'Gideon' in the unnamed fields part also has one truncated char.
    w = wma.WMADecoder(TestData.filepath('wma/test3_truncated_unicode.wma'))
    eq_(w.genre, 'Easy Listening')
    eq_(w.title, 'Gideon')
    
def test3_invalid_unicode_surregate():
    # This is the file has an invalid char (0xffff) in its WM/GENRE field. 'Gideon' in the 
    # unnamed fields part also has an invalid surregate (0xdbff and another 0xdbff).
    w = wma.WMADecoder(TestData.filepath('wma/test3_invalid_unicode_surregate.wma'))
    eq_(w.genre, '')
    eq_(w.title, '')
    
def test3_incomplete():
    # This file is truncated right in the middle of a field header. The error that it made was an
    # unpack error.
    w = wma.WMADecoder(TestData.filepath('wma/test3_incomplete.wma'))
    eq_(w.genre, '')
    eq_(w.title, '')
    
def test4():
    # VBR
    w = wma.WMADecoder(TestData.filepath('wma/test4.wma'))
    eq_(w.artist, 'Red Hot Chilly Peppers')
    eq_(w.album, '')
    eq_(w.title, 'Scar Tissue')
    eq_(w.genre, '')
    eq_(w.comment, '')
    eq_(w.year, '')
    eq_(w.track, 2)
    eq_(w.bitrate, 370)
    eq_(w.size, 673675)
    eq_(w.duration, 217)
    assert w.valid

def test5():
    # Another VBR
    w = wma.WMADecoder(TestData.filepath('wma/test5.wma'))
    eq_(w.bitrate, 303)
    eq_(w.duration, 295)
    
def test6():
    # Another VBR. This one had a huge, 30 seconds, duration gap
    w = wma.WMADecoder(TestData.filepath('wma/test6.wma'))
    eq_(w.bitrate, 422)
    eq_(w.duration, 298)
    
def test7():
    # Yet another VBR wma with buggy duration.
    w = wma.WMADecoder(TestData.filepath('wma/test7.wma'))
    eq_(w.bitrate, 327)
    eq_(w.duration, 539)

