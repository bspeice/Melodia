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

	def populate_metadata(self):
		"Populate the metadata of this song"
		#Will eventually use EchoNest to power this. For now, just use defaults.
		import datetime
		self.title        = "_"
		self.artist       = "_"
		self.album        = "_"
		self.release_date = datetime.datetime.now()
		self.genre        = "_"
		self.bpm          = 0

		self.bit_rate         = 0
		self.duration         = 0
		self.echonest_song_id = "_"
