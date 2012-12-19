from django.db import models
from Melodia import melodia_settings

"""
The Song model
Each instance of a Song represents a single music file.
This database model is used for storing the metadata information about a song,
and helps in doing sorting etc.
"""

class Song (models.Model):
	
	"""
	This class defines the fields and functions related to controlling
	individual music files.
	"""

	#Standard user-populated metadata
	title        = models.CharField(max_length = 64)
	artist       = models.CharField(max_length = 64)
	album        = models.CharField(max_length = 64)
	release_date = models.DateField()
	genre        = models.CharField(max_length = 64)
	bpm          = models.IntegerField()

	#File metadata
	bit_rate         = models.IntegerField()
	duration         = models.IntegerField()
	echonest_song_id = models.CharField(max_length = 64)
	url              = models.CharField(max_length = 64)
	file_hash        = melodia_settings.HASH_RESULT_DB_TYPE

	def populate_metadata(self, use_echonest = False, use_musicbrainz = False):
		"Populate the metadata of this song"
		import datetime

		if use_echonest:
			#Code to grab metadata from echonest here
			pass

		else:
			#Grab metadata for the database using what is in the track.
			from Melodia.resources import add_resource_dir
			add_resource_dir()

			import audiotools

			try:
				track                 = audiotools.open(self.url)
				track_metadata        = track.get_metadata()

				self.title            = track_metadata.track_name             or '<UNAVAILABLE>'
				self.artist           = track_metadata.artist_name            or '<UNAVAILABLE>'
				self.album            = track_metadata.album_name             or '<UNAVAILABLE>'
				self.release_date     = datetime.date(int(track_metadata.year or 1), 1, 1)
				self.bpm              = -1

				self.bit_rate         = track.bits_per_sample()               or '<UNAVAILABLE>'
				self.duration         = int(track.seconds_length())             or '<UNAVAILABLE>'
				self.echonest_song_id = ''

			except audiotools.UnsupportedFile, e:
				#Couldn't grab the local data
				#doesn't support the file, or because reading from it caused an error
				self.title            = "<UNAVAILABLE>"
				self.artist           = "<UNAVAILABLE>"
				self.album            = "<UNAVAILABLE>"
				self.release_date     = datetime.datetime.now()
				self.bpm              = -1

				self.bit_rate         = -1
				self.duration         = -1
				self.echonest_song_id = ''

		#Hash check is run regardless of what metadata method is used
		if self.file_hash == None:
			#Only get the hash if we really must, it's an expensive operation...
			from Melodia.melodia_settings import HASH_FUNCTION as hash
			f              = open(self.url, 'rb')
			self.file_hash = hash(f.read())
