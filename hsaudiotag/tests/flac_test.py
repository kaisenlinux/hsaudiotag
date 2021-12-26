# Created By: Virgil Dupras
# Created On: 2005/12/17
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .. import flac
from .util import TestData, eq_

#--- Metadata block header
def test_header_has_valid_attrs():
    fp = open(TestData.filepath('flac/test1.flac'), 'rb')
    fp.seek(4, 0) #the flac id is not a part of a block
    block = flac.MetaDataBlockHeader(fp)
    assert block.valid
    eq_(flac.STREAMINFO, block.type)
    assert not block.last_before_audio
    eq_(0x22, block.size)
    eq_(4, block.offset)
    assert isinstance(block.data(), flac.StreamInfo)
    fp.close()

def test_next():
    fp = open(TestData.filepath('flac/test1.flac'), 'rb')
    fp.seek(4, 0) #the flac id is not a part of a block
    header = flac.MetaDataBlockHeader(fp)
    assert header.valid
    eq_(flac.STREAMINFO, header.type)
    header = next(header)
    assert header.valid
    eq_(flac.SEEKTABLE, header.type)
    fp.close()

def test_next_until_eof():
    fp = open(TestData.filepath('flac/test1.flac'), 'rb')
    fp.seek(4, 0) #the flac id is not a part of a block
    header = flac.MetaDataBlockHeader(fp)
    count = 0
    while header.valid:
        count += 1
        header = next(header)
    eq_(4496, header.offset)
    eq_(4, count)
    fp.close()

#--- Metadata block
def test_valid_block():
    fp = open(TestData.filepath('flac/test1.flac'), 'rb')
    fp.seek(8, 0)
    refdata = fp.read(0x22)
    fp.seek(4, 0)
    header = flac.MetaDataBlockHeader(fp)
    block = header.data()
    eq_(refdata, block.data)
    fp.close()

#--- Stream info
def test_valid_stream_info():
    fp = open(TestData.filepath('flac/test1.flac'), 'rb')
    fp.seek(4, 0)
    header = flac.MetaDataBlockHeader(fp)
    block = header.data()
    eq_(44100, block.sample_rate)
    eq_(0x779958, block.sample_count)
    fp.close()

#--- Vorbis comment
def test_valid_vorbis_comment():
    fp = open(TestData.filepath('flac/test1.flac'), 'rb')
    fp.seek(4, 0)
    header = flac.MetaDataBlockHeader(fp)
    while header.type != flac.VORBIS_COMMENT:
        header = next(header)
    assert header.valid
    block = header.data()
    comment = block.comment
    eq_('Coolio', comment.artist)
    eq_('Country Line', comment.title)
    eq_('it takes a thief', comment.album)
    eq_(2, comment.track)
    eq_('It sucks', comment.comment)
    eq_('1994', comment.year)
    eq_('Hip-Hop', comment.genre)
    fp.close()

#--- FLAC
def test_test1():
    f = flac.FLAC(TestData.filepath('flac/test1.flac'))
    assert f.valid
    eq_(f.size, 123619)
    eq_(f.sample_rate, 44100)
    eq_(f.duration, 177)
    eq_(f.artist, 'Coolio')
    eq_(f.title, 'Country Line')
    eq_(f.album, 'it takes a thief')
    eq_(f.track, 2)
    eq_(f.comment, 'It sucks')
    eq_(f.year, '1994')
    eq_(f.genre, 'Hip-Hop')
    eq_(f.audio_offset, 0x1190)
    eq_(f.audio_size, 123619 - 0x1190)

def verify_emptyness(f):
    eq_(0, f.bitrate)
    eq_(0, f.sample_rate)
    eq_(0, f.sample_count)
    eq_(0, f.duration)
    eq_('', f.artist)
    eq_('', f.album)
    eq_('', f.title)
    eq_('', f.genre)
    eq_('', f.comment)
    eq_('', f.year)
    eq_(0, f.track)
    eq_(0, f.audio_offset)
    eq_(0, f.audio_size)

def test_invalid_zerofile():
    f = flac.FLAC(TestData.filepath('zerofile'))
    verify_emptyness(f)

def test_invalid_zerofill():
    f = flac.FLAC(TestData.filepath('zerofill'))
    verify_emptyness(f)

def test_invalid_randomfile():
    f = flac.FLAC(TestData.filepath('randomfile'))
    verify_emptyness(f)

def test_invalid_mp3():
    f = flac.FLAC(TestData.filepath('mpeg/test1.mp3'))
    verify_emptyness(f)

def test_invalid_wma():
    f = flac.FLAC(TestData.filepath('wma/test1.wma'))
    verify_emptyness(f)

def test_invalid_mp4():
    f = flac.FLAC(TestData.filepath('mp4/test1.m4a'))
    verify_emptyness(f)
