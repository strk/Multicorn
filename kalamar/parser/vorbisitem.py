# -*- coding: utf-8 -*-
# This file is part of Dyko
# Copyright © 2008-2009 Kozea
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Kalamar.  If not, see <http://www.gnu.org/licenses/>.

"""
Ogg/Vorbis parser.

This parser is read-only.

"""

try:
    from mutagen.oggvorbis import Open
except ImportError:
    import warnings
    warnings.warn('Can not import mutagen. '
                  'VorbisItem will not be available.',
                  ImportWarning)
else:
    from werkzeug import MultiDict
    from tempfile import NamedTemporaryFile
    from kalamar.item import Item

    class VorbisItem(Item):
        """Ogg/Vorbis parser.
        
        The vorbis format allows a lot of things for tagging. It is possible to
        add any label you want and, for each label, to put several values.
        Because of that, this module cannot guarantee a set of
        properties. Despite this, here are some common tags you can use:
        - time_length : duration in seconds
        - ogg_data : raw ogg/vorbis data
        - artist
        - genre
        - track
        
        """
        format = 'audio_vorbis'
        
        def _parse_data(self):
            """Parse Ogg/Vorbis metadata as properties."""
            properties = super(VorbisItem, self)._parse_data()
            properties['ogg_data'] = self._get_content()
            print self._get_content()
            
            # Create a real file descriptor, as VorbisFile does not accept a stream
            temporary_file = NamedTemporaryFile()
            temporary_file.write(properties['ogg_data'])
            temporary_file.seek(0)
            vorbis_tags = Open(temporary_file.name)
            
            for key in vorbis_tags:
                properties.setlist(key, vorbis_tags[key])
                
            temporary_file.close()
            
            if 'tracknumber' in properties:
                properties['tracknumber'] = int(properties['tracknumber'])
            
            return properties
        
        def serialize(self):
            """Return the whole file into a bytes string."""
            data = self.raw_parser_properties.get('ogg_data') \
                   or self._get_content()
            temporary_file = NamedTemporaryFile()
            temporary_file.write(data)
            
            vorbis_tags = Open(temporary_file.name)
            for key, values in self.raw_parser_properties.iterlists():
                if key != 'ogg_data':
                    vorbis_tags[key] = [unicode(value) for value in values]
            vorbis_tags.save()
            
            temporary_file.file.flush()
            temporary_file.seek(0)
            data = temporary_file.read()
            temporary_file.close()
            return data
        
