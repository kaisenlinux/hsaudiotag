# Created By: Virgil Dupras
# Created On: 2005/01/15
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..id3v2 import Id3v2, Header, POS_END, _read_id3_string
from .squeeze import expand_mpeg
from .util import TestData, eq_

def testNormal():
    tag = Id3v2(expand_mpeg(TestData.filepath('id3v2/normal.mp3')))
    eq_(tag.size,4096)
    eq_(tag.data_size,4086)
    assert tag.exists
    eq_(tag.flags, 0)
    eq_(tag.title,'La Primavera')
    eq_(tag.artist,'Manu Chao')
    eq_(tag.album,'Proxima Estacion Esperanza (AD')
    eq_(tag.year,'2001')
    eq_(tag.genre,'Latin')
    eq_(tag.comment,'http://www.EliteMP3.ws')

def testNotag():
    tag = Id3v2(expand_mpeg(TestData.filepath('id3v2/notag.mp3')))
    assert not tag.exists

def testThatspot():
    tag = Id3v2(TestData.filepath('id3v2/thatspot.tag'))
    expected_comment = """THAT SPOT RIGHT THERE (14 second demo clip)

This 14 second demo clip was recorded at CD-Quality using the standard MusicMatch Jukebox
software program.  If you like this track, you can click the "Buy CD" button in your MusicMatch
Jukebox "Track Info" window, and you'll be connected to a recommended online music retailer.


Enjoy your copy of MusicMatch Jukebox!"""
    eq_(tag.comment.replace('\r',''),expected_comment.replace('\r',''))
    eq_(tag.title,'That Spot Right There')
    eq_(tag.artist,'Carey Bell')
    eq_(tag.album,'Mellow Down Easy')
    eq_(tag.year,'')
    eq_(tag.genre,'Blues')

def testOzzy():
    tag = Id3v2(TestData.filepath('id3v2/ozzy.tag'))
    eq_(tag.title,'Bark At The Moon')
    eq_(tag.artist,'Ozzy Osbourne')
    eq_(tag.album,'Bark At The Moon')
    eq_(tag.year,'1983')
    eq_(tag.genre,'Metal')
    eq_(tag.comment,'None')
    eq_(tag.track,1)

def testUnicode():
    tag = Id3v2(TestData.filepath('id3v2/230-unicode.tag'))
    eq_(tag.frames['TXXX'].data.text,'example text frame\nThis text and the description should be in Unicode.')

def testWithFooter():
    tag = Id3v2(expand_mpeg(TestData.filepath('id3v2/with_footer.mp3')))
    assert tag.exists
    eq_(tag.artist,'AFI')
    eq_(tag.position,POS_END)

def testTrack():
    tag = Id3v2(expand_mpeg(TestData.filepath('id3v2/test_track.mp3')))
    eq_(tag.track,1)

def testZeroFile():
    tag = Id3v2(TestData.filepath('zerofile'))
    assert not tag.exists

def test_non_ascii_non_unicode():
    #Test a v2 tag with non-ascii char in a non-unicode string
    tag = Id3v2(TestData.filepath('id3v2/ozzy_non_ascii.tag'))
    assert isinstance(tag.title,str)
    eq_(tag.title,'Bark At The \u00c8\u00c9\u00ca\u00cb')

def test_numeric_genre():
    #A file with a genre field containing (<number>)
    tag = Id3v2(TestData.filepath('id3v2/numeric_genre.tag'))
    eq_('Metal',tag.genre)

def test_numeric_genre2():
    #A file with a genre field containing (<number>)
    tag = Id3v2(TestData.filepath('id3v2/numeric_genre2.tag'))
    eq_('Rock',tag.genre)

def test_numeric_genre3():
    #like numeric_genre, but the number is not between ()
    tag = Id3v2(TestData.filepath('id3v2/numeric_genre3.tag'))
    eq_('Rock',tag.genre)

def test_unicode_truncated():
    tag = Id3v2(TestData.filepath('id3v2/230-unicode_truncated.tag'))
    eq_(tag.frames['TXXX'].data.text,
        'example text frame\nThis text and the description should be in Unicode.')

def test_unicode_invalid_surregate():
    tag = Id3v2(TestData.filepath('id3v2/230-unicode_surregate.tag'))
    eq_(tag.frames['TXXX'].data.text,'')

def test_unicode_comment():
    tag = Id3v2(TestData.filepath('id3v2/230-unicode_comment.tag'))
    eq_(tag.frames['COMM'].data.title,'example text frame')
    eq_(tag.frames['COMM'].data.text,
        'This text and the description should be in Unicode.')
    eq_(tag.comment,
        'This text and the description should be in Unicode.')

def test_TLEN():
    tag = Id3v2(TestData.filepath('mpeg/test8.mp3'))
    eq_(tag.duration,299)

def test_DecodeTrack():
    tag = Id3v2(TestData.filepath('zerofile'))
    method = tag._decode_track
    eq_(42,method('42'))
    eq_(0,method(''))
    eq_(12,method('12/24'))
    eq_(0,method(' '))
    eq_(0,method('/'))
    eq_(0,method('foo/12'))

def test_Decodeduration():
    tag = Id3v2(TestData.filepath('zerofile'))
    tag._get_frame_text = lambda _:'4200'
    eq_(4,tag.duration)
    tag._get_frame_text = lambda _:''
    eq_(0,tag.duration)
    tag._get_frame_text = lambda _:'foo'
    eq_(0,tag.duration)

def test_newlines():
    tag = Id3v2(TestData.filepath('id3v2/newlines.tag'))
    eq_('foo bar baz',tag.title)
    eq_('foo bar baz',tag.artist)
    eq_('foo bar baz',tag.album)
    eq_('foo bar baz',tag.genre)
    eq_('foo bar baz',tag.year)
    eq_('foo\nbar\rbaz',tag.comment)

def test_version_22():
    tag = Id3v2(TestData.filepath('id3v2/v22.tag'))
    eq_('Chanson de Nuit - Op. 15 No. 1',tag.title)
    eq_('Kennedy / Pettinger',tag.artist)
    eq_('Salut d\'Amour (Elgar)',tag.album)
    assert tag.comment != ''
    assert tag.track != '5/10'
    eq_('1984',tag.year)
    eq_('Classical',tag.genre)

def test_v24_no_syncsafe():
    #syncsafe is only for v2.4 and up.
    tag = Id3v2(TestData.filepath('id3v2/v24_no_syncsafe.tag'))
    eq_('Boccherini / Minuet (String Quartet in E major)',tag.title)

def test_stringtype_one_be_encoded_no_bom():
    # Stringtype 1 is supposed to be utf-16 with a BOM. However, some tags have this string type
    # with no BOM. the 'utf-16' encoding defaults to native byte order when it happens.
    # On BE machines, it results in a badly interpreted tag. I've tried hard to fake a BE 
    # machine here, but it didn't work, so this test is kind of worthless unless ran on a BE 
    # machine.
    eq_('foobar', _read_id3_string('foobar'.encode('utf-16le'), 1))

def test_invalid_text_ype():
    # invalid_text_type has a 0xff stringtype
    # Don't crash on invalid string types, just ignore the text
    tag = Id3v2(TestData.filepath('id3v2/invalid_text_type.tag')) # don't crash
    eq_(tag.frames['TXXX'].data.text, '') # ignore text

def test_invalid_comment_type():
    # invalid_comment_type has a 0xff stringtype
    # Don't crash on invalid string types, just ignore the text
    tag = Id3v2(TestData.filepath('id3v2/invalid_comment_type.tag')) # don't crash
    eq_(tag.frames['COMM'].data.text, '') # ignore text

def test_id3v2_header():
    fp = open(TestData.filepath('id3v2/230-unicode_comment.tag'),'rb')
    h = Header(fp)
    assert h.valid
    fp.close()
