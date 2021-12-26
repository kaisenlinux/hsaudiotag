# Created By: Virgil Dupras
# Created On: 2005/12/16
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from struct import unpack
import re

from .util import FileOrPath

RE_STARTS_WITH_DIGIT = re.compile(r"^\d+")

class InvalidFileError(Exception):
    pass

class VorbisPage:
    OGG_PAGE_ID = b'OggS'
    BASE_SIZE = 0x1b
    MAX_SIZE = 0x1b + 0xff
    def __init__(self, fp):
        self.fp = fp
        self.start_offset = fp.tell()
        data = fp.read(self.MAX_SIZE)
        page_id, version, type, pos1, pos2, serial, page_number, checksum, segment_count = \
            unpack('<4s2B5IB',data[:self.BASE_SIZE])
        position = (pos2 << 32) + pos1
        self.valid = page_id == self.OGG_PAGE_ID
        self.page_number = page_number
        self.position = position
        segments = data[self.BASE_SIZE:self.BASE_SIZE+segment_count]
        page_size = sum(segments)
        self.size = page_size
        self.header_size = self.BASE_SIZE + segment_count
    
    def __next__(self):
        self.fp.seek(self.start_offset + self.header_size + self.size)
        return VorbisPage(self.fp)
    
    def read(self):
        self.fp.seek(self.start_offset + self.header_size)
        return self.fp.read(self.size)
    

class VorbisComment:
    def __init__(self, data):
        def get_field(field_name):
            try:
                data = meta_data[field_name]
            except KeyError:
                data = meta_data.get(field_name.lower(), b'')
            return str(data, 'utf-8')
        
        [vendor_string_length] = unpack('<I', data[:4])
        meta_data_offset = vendor_string_length + 4
        [meta_count] = unpack('<I', data[meta_data_offset:meta_data_offset+4])
        meta_data = {}
        offset = meta_data_offset + 4
        for _ in range(meta_count):
            [length] = unpack('<I',data[offset:offset+4])
            value = data[offset+4:offset+length+4]
            splitted = value.split(b'=')
            meta_data[splitted[0]] = splitted[1]
            offset += length + 4
        self.artist = get_field(b'ARTIST')
        self.album = get_field(b'ALBUM')
        self.title = get_field(b'TITLE')
        self.genre = get_field(b'GENRE')
        track_str = get_field(b'TRACKNUMBER')
        m = RE_STARTS_WITH_DIGIT.match(track_str)
        self.track = int(m.group(0)) if m else 0
        self.comment = get_field(b'COMMENT')
        self.year = get_field(b'DATE')
        if not self.year:
            description = get_field(b'DESCRIPTION')
            if 'YEAR: ' in description:
                index = description.find('YEAR: ')
                self.year = description[index+6:index+10]
    

class Vorbis:
    def __init__(self, infile):
        with FileOrPath(infile, 'rb') as fp:
            try:
                self._read(fp)
            except Exception: #The unpack error doesn't seem to have a class. I have to catch all here
                self._empty()
    
    def _empty(self):
        self.valid = False
        self.bitrate = 0
        self.artist = ''
        self.album = ''
        self.title = ''
        self.genre = ''
        self.year = ''
        self.comment = ''
        self.track = 0
        self.sample_rate = 0
        self.sample_count = 0
        self.duration = 0
        self.audio_offset = 0
        self.audio_size = 0
    
    def _read(self, fp):
        fp.seek(0, 2)
        self.size = fp.tell()
        fp.seek(0, 0)
        #Read 1st page
        page = VorbisPage(fp)
        if not page.valid:
            raise InvalidFileError()
        data = page.read()
        unpacked = unpack('<7sIB4I2B', data[:30])
        (file_id, version, channel_mode, sample_rate, bitrate_max, bitrate_nominal, bitrate_max, 
            block_size, stop_flag) = unpacked
        if file_id != b'\x01vorbis':
            raise InvalidFileError()
        self.sample_rate = sample_rate
        self.bitrate = bitrate_nominal // 1000
        
        #Read 2nd page
        page = next(page)
        if not page.valid:
            raise InvalidFileError()
        data = page.read()
        if data[:7] != b'\x03vorbis':
            raise InvalidFileError()
        comment = VorbisComment(data[7:])
        self.artist = comment.artist
        self.album = comment.album
        self.title = comment.title
        self.track = comment.track
        self.year = comment.year
        self.genre = comment.genre
        self.comment = comment.comment
        
        #Get third page for audio_offset
        page = next(page)
        if not page.valid:
            raise InvalidFileError()
        self.audio_offset = page.start_offset
        self.audio_size = self.size - self.audio_offset
        
        #Seek last page to get sample count. It's impossible to not have at least one page in
        #the last 64kb.
        fp.seek(-0x10000, 2)
        last_data = fp.read()
        last_offset = last_data.rfind(VorbisPage.OGG_PAGE_ID)
        to_seek = 0x10000 - last_offset
        fp.seek(-to_seek, 2)
        page = VorbisPage(fp)
        if not page.valid:
            raise InvalidFileError()
        self.sample_count = page.position
        self.duration = self.sample_count // self.sample_rate
        self.valid = True
    
