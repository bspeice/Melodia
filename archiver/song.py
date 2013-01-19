from django.db import models
from Melodia import melodia_settings

import datetime
"""
The Song model
Each instance of a Song represents a single music file.
This database model is used for storing the metadata information about a song,
and helps in doing sorting etc.
"""

_default_title        = "_UNAVAILABLE_"
_default_artist       = "_UNAVAILABLE_"
_default_album        = "_UNAVAILABLE_"
_default_release_date = datetime.datetime.now #Function will be called per new song, rather than only being called right now.
_default_genre        = "_UNAVAILABLE_"
_default_bpm          = -1
_default_disc_number  = -1
_default_disc_total   = -1
_default_track_number = -1
_default_track_total  = -1

_default_bit_rate         = -1
_default_duration         = -1
_default_echonest_song_id = ""

class Song (models.Model):
	
	"""
	This class defines the fields and functions related to controlling
	individual music files.
	Note that the Playlist model depends on this model's PK being an int.
	"""

	#Standard user-populated metadata
	title        = models.CharField(max_length = 64, default            = _default_title)
	artist       = models.CharField(max_length = 64, default            = _default_artist)
	album        = models.CharField(max_length = 64, default            = _default_album)
	release_date = models.DateField(default    = _default_release_date)
	genre        = models.CharField(max_length = 64, default            = _default_genre)
	bpm          = models.IntegerField(default = _default_bpm)
	disc_number  = models.IntegerField(default = _default_disc_number)
	disc_total   = models.IntegerField(default = _default_disc_total)
	track_number = models.IntegerField(default = _default_track_number)
	track_total  = models.IntegerField(default = _default_track_total)

	#File metadata
	bit_rate         = models.IntegerField(default = _default_bit_rate)
	duration         = models.IntegerField(default = _default_bit_rate)
	echonest_song_id = models.CharField(max_length = 64, default = _default_echonest_song_id)
	url              = models.CharField(max_length = 255)
	file_hash        = melodia_settings.HASH_RESULT_DB_TYPE

	def _file_not_changed(self):
		"Make sure the hash for this file is valid - return True if it has not changed."
		#Overload the hash function with whatever Melodia as a whole is using
		from Melodia.melodia_settings import HASH_FUNCTION as hash

		#Check if there's a hash entry - if there is, the song may not have changed,
		#and we can go ahead and return
		if self.file_hash != None:
			song_file = open(self.url, 'rb')
			current_file_hash = hash(song_file.read())

			if current_file_hash == self.file_hash:
				#The song data hasn't changed at all, we don't need to do anything
				return True

		return False

	def _grab_metadata_echonest(self):
		"Populate this song's metadata using EchoNest"
		pass

	def _grab_metadata_local(self):
		"Populate this song's metadata using what is locally available"
		#It's weird, but we need to wrap importing audiotools
		from Melodia.resources import add_resource_dir
		add_resource_dir()
		import audiotools

		try:
			track                 = audiotools.open(self.url)
			track_metadata        = track.get_metadata()

			self.title        = track_metadata.track_name  or _default_title
			self.artist       = track_metadata.artist_name or _default_artist
			self.album        = track_metadata.album_name  or _default_album
			self.release_date = datetime.date(int(track_metadata.year or 1), 1, 1)
			self.track_number = track_metadata.track_number or _default_track_number
			self.track_total  = track_metadata.track_total  or _default_track_total
			self.disc_number  = track_metadata.album_number or _default_disc_number
			self.disc_total   = track_metadata.album_total  or _default_disc_total
			self.bpm          = _default_bpm

			self.bit_rate         = track.bits_per_sample() or _default_bit_rate
			self.duration         = int(track.seconds_length()) or _default_duration
			self.echonest_song_id = _default_echonest_song_id

		except audiotools.UnsupportedFile, e:
			#Couldn't grab the local data - fill in the remaining data for this record, preserving
			#anything that already exists.
			self.title            = self.title            or _default_title
			self.artist           = self.artist           or _default_artist
			self.album            = self.album            or _default_album
			self.release_date     = self.release_date     or _default_release_date()

			self.bpm              = self.bpm              or _default_bpm
			self.bit_rate         = self.bit_rate         or _default_bitrate
			self.duration         = self.bit_rate         or _default_duration
			self.echonest_song_id = self.echonest_song_id or _default_echonest_song_id

	def populate_metadata(self, use_echonest = False):
		"Populate the metadata of this song (only if file hash has changed), and save the result."
		if self._file_not_changed():
			return

		#If we've gotten to here, we do actually need to fully update the metadata
		if use_echonest:
			self._grab_echonest()

		else:
			self._grab_metadata_local()
			
	def convert(self, output_location, output_format, progress_func = lambda x, y: None):
		"Convert a song to a new format."
		#Note that output_format over-rides the format guessed by output_location

		from Melodia.resources import add_resource_dir
		add_resource_dir()

		import audiotools

		convert_from = audiotools.open(self.url)
		convert_from.convert(output_location,
								output_format,
								progress_func)

