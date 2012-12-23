
"""
This file contains settings specifically for Melodia.
The reason this was created is to control settings specifically for Melodia,
as opposed to Django at large.
"""

#Format of this variable is a Django choices field
SUPPORTED_AUDIO_FILETYPES = (
		('MP3', 'MPEG Layer 3'),
		('OGG', 'Ogg Vorbis Audio'),
	)

#Use a list comprehension to grab the file extensions from our supported types
SUPPORTED_AUDIO_EXTENSIONS = [ filetype[0] for filetype in SUPPORTED_AUDIO_FILETYPES ]

#Note that you can change this to any function you want, any
#time hashing is used by Melodia, this function is referenced
import django.db.models.fields

HASH_FUNCTION       = hash
HASH_RESULT_DB_TYPE = django.db.models.fields.IntegerField(default =  -1)
