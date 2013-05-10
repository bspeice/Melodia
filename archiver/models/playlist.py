"""
The Playlist model is simply that - it's a playlist of songs. However, we do
have to guarantee the song order, in addition to re-ordering the playlist.
As such, a :class:`models.ManyToManyField` isn't sufficient. We use a custom
database field to store a list of integers - the :class:`IntegerListField`.
This way we can guarantee song order, re-order the playlist, have songs
appear multiple times, etc.
"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from song import Song
from archiver.listfield import IntegerListField

import re
from warnings import warn

class Playlist(models.Model):
	class Meta:
		app_label = 'archiver'

	"""
	.. data:: name

	   String with the human-readable name for this playlist.

	.. data:: song_list

	   List made up of Python integers. Each integer is assumed
	   to be a primary key to the :data:`Song.id` field for a song.
	"""

	name       = models.CharField(max_length = 255)
	song_list = IntegerListField()

	def insert(self, position, new_song):
		"""
		Insert a new song into the playlist at a specific position.

		:param position: **Index** for the position this new song should be inserted at.
		:param new_song: Reference to a :class:`Song` instance that will be inserted.
		"""

		if not isinstance(new_song, Song):
			#Not given a song reference, raise an error
			raise ValidationError("Not given a song reference to insert.")
			
		self.song_list.insert(position, new_song.id)

	def append(self, new_song):
		"""
		Add a new song to the end of the playlist.

		:param new_song: Reference to a :class:`Song` instance to be appended.
		"""

		if not isinstance(new_song, Song):
			#Not given a song reference, raise an error
			raise ValidationError("Not given a song reference to insert.")

		self.song_list.append(new_song.id)

	def move(self, original_position, new_position):
		"""
		Move a song from one position to another

		:param original_position: The index of the song we want to move
		:param new_position: The index of where the song should be. See note below.

		.. note::

		   When moving songs, it's a bit weird since the index we're actually
		   moving to may change. Consider the scenario --

		      * Function called with indexes 4 and 6

		      * Song removed from index 4 

		        * The song that was in index 6 is now at index 5

		      * Song inserted at index 6 in new list - one further than originally intended.

		   As such, the behavior is that the song at index ``original_position`` is placed
		   above the song at ``new_position`` when this function is called.
		"""
		if original_position == new_position:
			return

		song_id = self.song_list[original_position]

		if new_position < original_position:
			del self.song_list[original_position]
			self.song_list.insert(new_position, song_id)

		else:
			del self.song_list[original_position]
			self.song_list.insert(new_position - 1, song_id) #Account for the list indices shifting down.

	def remove(self, position):
		"""
		Remove a song from this playlist.

		:param position: Index of the song to be removed
		"""
		if position > len(self.song_list):
			return False

		del self.song_list[position]

	def export(self, playlist_type = "m3u"):
		"""
		Export this internal playlist to a file format.
		Supported formats:

		   * pls
		   * m3u

		:param playlist_type: String containing the file type to export to
		:rtype: String containing the file content for this playlist.
		"""

		if playlist_type == "pls":
			#Playlist header
			playlist_string = "[playlist]"

			#Playlist body
			for index, song_id in enumerate(self.song_list):
				song = self.songs.get(id = song_id)

				playlist_string += "File" + str(index + 1) + "=" + song.url + "\n"
				playlist_string += "Title" + str(index + 1) + "=" + song.title + "\n"
				playlist_string += "Length" + str(index + 1) + "=" + str(song.duration) + "\n"

			#Playlist footer
			playlist_string += "NumberOfEntries=" + str(len(self.song_list))
			playlist_string += "Version=2"
			return playlist_string

		elif playlist_type == "m3u":
			#Playlist header
			playlist_string += "#EXTM3U" + "\n"

			#Playlist body
			for song_id in self.song_list:
				song = self.songs.get(id = song_id)

				playlist_string += "#EXTINF:" + str(song.duration) + "," + song.artist + " - " + song.title + "\n"
				playlist_string += song.url + "\n\n"

			return playlist_string

	def playlist_import(self, playlist_string = None):
		"""
		Import and convert a playlist into native DB format.

		:param playlist_string: A string with the file content we're trying to import.

		:rtype: Returns true of the playlist format was recognized. See notes on processing below.

		.. warning::

		   The semantics on returning are nitpicky. This function will return ``False`` if the
		   playlist format was not recognized. If there are errors in processing, this
		   function will still return ``True``.

		   For example, if you try to import a song which does not exist in an :class:`Archive`,
		   it will fail that song silently.

		.. todo::

		   Actually write the import code.
		"""
		#TODO: Code playlist importing
		self.song_list = []
		if not playlist_string:
			#Make sure we have a string to operate on.
			return False

		#Figure out what format we're in
		if playlist_string[0:7] == "#EXTM3U":
			#Import m3u format playlist
			print playlist_string

			#Expected format is "#EXTINF:" followed by the song url on the next line.
			line_iterator = playlist_string.split("\n").__iter__()

			#In case we end iteration early
			try:
				for line in line_iterator:

					if line[0:8] == "#EXTINF:":
						song_url = line_iterator.next() #Consume the next line

						try:
							song = Song.objects.get(url = song_url)
							self.append(song)

						except ObjectDoesNotExist:
							#The URL of our song could not be found
							warn("The playlist entry: " + song_url + " could not be found, and has not been added to your playlist.")
							continue

			#Silently end processing
			except StopIteration:
				pass

			return True

		if playlist_string[0:10] == "[playlist]":
			#Import pls format playlist
			#This one is a bit simpler - we're just looking for lines that start with "File="
			pls_regex = re.compile("^File=", re.IGNORECASE)

			for file_line in pls_regex.match(pls_regex, playlist_string):
				song_url = file_line[5:]
				try:
					song = Song.objects.get(url = song_url)
					self.append(song)

				except ObjectDoesNotExist:
					#The URL of our song could not be found
					warn("The playlist entry: " + song_url + " could not be found, and has not been added to your playlist.")
					continue

			return True

		#If we got here, the playlist format wasn't recognized.
		return False
