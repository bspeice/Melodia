"""
The :class:`Song` model is by far the most complicated and involved model.
Each instance is a single music file. This model is used to store metadata
about the song.
"""

from django.db import models
from Melodia import melodia_settings

from archive import Archive

import datetime
import os.path

_default_string = "_UNAVAILABLE_"
_default_date   = datetime.datetime.now
_default_int    = -1

_default_rating = 0
_default_rating_bad       = 1
_default_rating_ok        = 2
_default_rating_decent    = 3
_default_rating_good      = 4
_default_rating_excellent = 5
_default_rating_choices = (
		(_default_rating, 'Default'),
		(_default_rating_bad, 'Bad'),
		(_default_rating_ok, 'OK'),
		(_default_rating_decent, 'Decent'),
		(_default_rating_good, 'Good'),
		(_default_rating_excellent, 'Excellent'),
		)

class Song (models.Model):
	"""
	.. data:: title
	   
	   Title tag of this song

	.. data:: artist

	   Artist tag of this song.

	.. data:: album_artist

	   Album artist tag of this song. Can be used to group albums where
	   individual songs were made by different people.

	.. data:: album

	   Album tag of this song.

	.. data:: year
	
	   Integer representing the year this song was made.

	.. data:: genre

	   Genre tag of this song. This is a general :class:`models.CharField`
	   field, and is not limited to a specific set of genres.

	.. data:: bpm

	   Beats per minute of this song (integer).

	.. data:: disc_number

	   Disc number this song came from

	.. data:: disc_total

	   Total number of discs in the album this song is from

	.. data:: track_number

	   Track number in the album this song is from

	.. data:: track_total

	   Total number of tracks in the album this song is from

	.. data:: comment

	   Comment tag of this song

	.. data:: bit_rate

	   Integer representing the bit rate of this song

	.. data:: duration
	
	   Duration (in seconds, floating-point value) of this song

	.. data:: add_date

	   Date (not time) this song was added to the DB. Should **not** be
	   modified outside of this class' methods.

	.. data:: url

	   URL for where this file is located on disk.

	.. data:: file_hash

	   The hash string for this file - used to quickly check if the file has
	   been modified.

	.. data:: file_size

	   Size of the file in bytes.

	.. data:: play_count

	   How many times this file has been played through (defined as greater
	   than 50% of the song heard before skipping)

	.. data:: skip_count

	   How many times this file has been skipped (defined as less than 50% of
	   the song heard before skipping)

	.. data:: rating

	   Rating for this song. Ratings are as follows in order of increasing favoredness 
	   on a 1--5 scale --

	   =========    ========    ================
	   Rating:      Value:      Class field:
	   =========    ========    ================
	   Default      0           RATING_DEFAULT
	   Bad          1           RATING_BAD
	   OK           2           RATING_OK
	   Decent       3           RATING_DECENT
	   Good         4           RATING_GOOD
	   Excellent    5           RATING_EXCELLENT
	   =========    ========    ================

	.. todo:: 

	   Change defaults to allow for ``None`` instead
	   Change private functions to public as need be
	"""

	#Standard song metadata
	title        = models.CharField(max_length = 64, default = _default_string)
	artist       = models.CharField(max_length = 64, default = _default_string)
	album_artist = models.CharField(max_length = 64, default = _default_string)
	album        = models.CharField(max_length = 64, default = _default_string)
	year         = models.IntegerField(default = _default_string)
	genre        = models.CharField(max_length = 64, default = _default_string)
	bpm          = models.IntegerField(default = _default_int)
	disc_number  = models.IntegerField(default = _default_int)
	disc_total   = models.IntegerField(default = _default_int)
	track_number = models.IntegerField(default = _default_int)
	track_total  = models.IntegerField(default = _default_int)
	comment      = models.CharField(default = _default_string, max_length=512)

	#File metadata
	bit_rate         = models.IntegerField(default = _default_int)
	duration         = models.FloatField(default = _default_int)
	add_date         = models.DateField(default = _default_date)
	url              = models.CharField(max_length = 255)
	file_hash        = melodia_settings.HASH_RESULT_DB_TYPE
	file_size        = models.IntegerField(default = _default_int)

	#Melodia metadata
	play_count = models.IntegerField(default = _default_int)
	skip_count = models.IntegerField(default = _default_int)
	rating     = models.IntegerField(default = _default_int, choices = _default_rating_choices)

	#Link back to the archive this comes from
	parent_archive = models.ForeignKey(Archive)

	#Set a static reference to the rating options
	RATING_DEFAULT   = _default_rating
	RATING_BAD       = _default_rating_bad
	RATING_OK        = _default_rating_ok
	RATING_DECENT    = _default_rating_decent
	RATING_GOOD      = _default_rating_good
	RATING_EXCELLENT = _default_rating_excellent

	class Meta:
		app_label = 'archiver'

	def _get_full_url(self):
		"Combine this song's URL with the URL of its parent"
		return os.path.join(parent_archive.root_folder, self.url)

	def _file_not_changed(self):
		"Make sure the hash for this file is valid - return True if it has not changed."
		#Overload the hash function with whatever Melodia as a whole is using
		from Melodia.melodia_settings import HASH_FUNCTION as hash

		#Check if there's a hash entry - if there is, the song may not have changed,
		#and we can go ahead and return
		if self.file_hash != None:
			song_file = open(self._get_full_url, 'rb')
			current_file_hash = hash(song_file.read())

			if current_file_hash == self.file_hash:
				#The song data hasn't changed at all, we don't need to do anything
				return True

		return False

	def _grab_file_info(self):
		"Populate file-based metadata about this song."
		import os
		#Overload the hash function with whatever Melodia as a whole is using
		from Melodia.melodia_settings import HASH_FUNCTION as hash
		
		file_handle = open(self._get_full_url, 'rb')
		
		self.file_hash = hash(file_handle.read())
		self.file_size = os.stat(self._get_full_url).st_size

	def _grab_metadata_local(self):
		"Populate this song's metadata using what is locally available"
		#Use mutagen to get the song metadata
		import mutagen

		try:
			#Use mutagen to scan local metadata - don't update anything else (i.e. play_count)
			track             = mutagen.File(self._get_full_url)
			track_easy        = mutagen.File(self._get_full_url, easy=True)

			self.title        = track_easy['title'][0]  or _default_string
			self.artist       = track_easy['artist'][0] or _default_string
			self.album_artist = track_easy['albumartist'][0] or _default_string
			self.album        = track_easy['album'][0]  or _default_string
			self.year         = int(track_easy['date'][0][0:4]) or _default_int
			self.genre        = track_easy["genre"][0] or _default_string

			self.disc_number  = int(track_easy['discnumber'][0].split('/')[0]) or _default_int
			self.disc_total   = int(track_easy['discnumber'][0].split('/')[-1]) or _default_int
			self.track_number = int(track_easy['track_number'][0].split('/')[0]) or _default_int
			self.track_total  = int(track_easy['track_number'][0].split('/')[-1])  or _default_int
			self.comment      = track_easy['comment'][0] or _default_string

			self.bit_rate         = track.info.bitrate or _default_int
			self.duration         = track.info.length or _default_int

		except:
			#Couldn't grab the local data
			return False

	def populate_metadata(self):
		"""
		Populate the metadata of this song (only if file hash has changed), and save the result.
		"""
		if self._file_not_changed():
			return

		#If we've gotten to here, we do actually need to fully update the metadata
		if use_echonest:
			self._grab_echonest()

		else:
			self._grab_metadata_local()
			
	def convert(self, output_location, output_format):
		"""
		Convert a song to a new format.

		:param output_location: String URL of where the resulting file should be stored
		:param output_format: Output format of the resulting file

		.. todo::

		   Actually write the code to convert files, or abandon if necessary
		"""
		pass #Need to get pydub code in place
