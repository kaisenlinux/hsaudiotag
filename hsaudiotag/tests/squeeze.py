# coding: utf-8 
# Created By: Virgil Dupras
# Created On: 2009-06-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# A problem with hsaudiotag is that the test data used from test units is usually copyrighted music.
# Another problem is that they are usually big files. But, since this module only cares about
# metadata, we can get rid of the content itself. This unit serves this purpose. It replaces content
# with placeholders, which will be expanded back with null data when the test unit needs the file.

import re
from io import BytesIO
from struct import unpack

from .. import mpeg, id3v2, mp4

def squeeze_mpeg(inpath, outpath):
    # takes the file in `inpath`, squeezes it, and put the result in `outpath`
    s = open(inpath, 'rb').read()
    infile = BytesIO(s)
    tag = id3v2.Id3v2(infile)
    start_offset = tag.size if (tag.exists and tag.position == id3v2.POS_BEGIN) else 0
    infile.seek(start_offset, 0)
    fb = mpeg.FrameBrowser(infile)
    # we don't want to squeeze the first frame because it might be a VBR header, which we want to
    # keep intact
    if not next(fb).valid:
        fb._seek()
    result = s[:fb.position] # add whatever's before the mpeg frames
    frames = b''
    last_pos = fb.position
    # add all mpeg frame headers except the last (sometimes, the last frame is cut off. we don't
    # want to squeeze it, but to keep it intact.)
    while fb.frame.valid:
        frames += s[fb.position:fb.position+4]
        last_pos = fb.position
        next(fb)
    frames = frames[:-4] # remove the last frame
    if not frames:
        print('Couldn\'t find frames', fb.position)
    frame_count = len(frames) // 4
    result += ('[SQUEEZED_FRAMES:%d]' % frame_count).encode('ascii')
    result += frames
    result += s[last_pos:] # add whatever's after the mpeg frames
    outfile = open(outpath, 'wb')
    outfile.write(result)

def expand_mpeg(filename):
    # takes the squeezed `filename`, expands it, and returns a file-like object
    infile = open(filename, 'rb')
    s = infile.read()
    re_squeezed = re.compile(r'\[SQUEEZED_FRAMES:(\d+?)\]')
    match = re_squeezed.search(str(s, 'latin-1'))
    if match is None:
        return BytesIO(s)
    result = BytesIO()
    result.write(s[:match.start()])
    frame_count = int(match.groups()[0])
    frame_string = s[match.end():match.end()+frame_count*4]
    frames = []
    for i in range(frame_count):
        frame_data_string = frame_string[i*4:i*4+4]
        frame_data = unpack('!I', frame_data_string)[0]
        h = mpeg.MpegFrameHeader(frame_data)
        assert h.valid
        frames.append(frame_data_string + (b'\0' * (h.size - 4)))
    frames = b''.join(frames)
    result.write(frames)
    result.write(s[match.end()+frame_count*4:])
    result.seek(0, 0)
    return result

def squeeze_mp4(inpath, outpath):
    # takes the file in `inpath`, squeezes it, and put the result in `outpath`
    s = open(inpath).read()
    m = mp4.File(inpath)
    [mdat] = [a for a in m.atoms if (a.size > 8) and (a.type == 'mdat')]
    data_offset = mdat.start_offset + mp4.HEADER_SIZE
    data_size = mdat.content_size
    before = s[:data_offset]
    after = s[data_offset + data_size:]
    result = ''.join([before, '[SQUEEZED_BYTES:%d]' % data_size, after])
    outfile = open(outpath, 'w')
    outfile.write(result)

def expand_mp4(filename):
    # takes the squeezed `filename`, expands it, and returns a file-like object
    infile = open(filename, 'rb')
    s = infile.read()
    re_squeezed = re.compile(r'\[SQUEEZED_BYTES:(\d+?)\]')
    match = re_squeezed.search(str(s, 'latin-1'))
    if match is None:
        return BytesIO(s)
    result = BytesIO()
    result.write(s[:match.start()])
    byte_count = int(match.groups()[0])
    result.write(b'\0' * byte_count)
    result.write(s[match.end():])
    result.seek(0, 0)
    return result
