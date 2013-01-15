from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from song import Song
from listfield import IntegerListField

import re
from warnings import warn

"""
Playlist model
Each playlist is a high-level ordering of songs. There really isn't much to a playlist - just its name, and the songs inside it.
However, we need to have a way to guarantee song order, in addition to re-ordering. A ManyToMany field can't do this.
As such, a custom IntegerListField is implemented - it takes a python list of ints, converts it to a text field in the DB,
and then back to a python list. This way, we can guarantee order, and have a song appear multiple times.
The IntegerListField itself uses the ID of each song as the int in a list. For example, a list of:
	[1, 3, 5, 17]

Means that the playlist is made up of four songs. The order of the playlist is the song with index 1, 3, 5, and 17.
Additionally, the ManyToMany field is included to make sure we don't use the global Songs manager - it just seems hackish.
"""

class Playlist (models.Model):
	"""
	The Playlist class defines the playlist model and its operations.
	Currently supported are add, move, and remove operations, as well as exporting to
	multiple formats.
	"""

	name       = models.CharField(max_length = 255)
	song_list = IntegerListField()

	#This is a bit of a backup field, since technically the song PK's are in
	#the song_order field. However, it might be useful to just get a reference
	#to the songs in this playlist. Additionally, it's kind of hackish to reference
	#the global Song manager, rather than something that is specific for this playlist.
	songs      = models.ManyToManyField(Song)

	def _populate_songs(self):
		"""
		Make sure that the 'songs' relation is up-to-date.
		"""
		#This operation works by getting the ID's for all songs currently in the playlist,
		#calculates what we need to add, what we need to remove, and then does it.
		#As much work as is possible is done on the python side to avoid the DB at all costs.
		current_song_ids     = [song.id for song in self.songs.all()]
		current_song_ids_set = set(current_song_ids)

		new_song_ids_set = set(self.song_list)

		remove_set = current_song_ids_set.difference(new_song_ids_set)
		add_set    = new_song_ids_set.difference(current_song_ids_set)

		for song_id in remove_set:
			song = self.songs.get(id = song_id)
			song.remove()

		for song_id in add_set:
			song = Song.objects.get(id = song_id) #Using the global Songs manager is unavoidable for this one
			self.songs.add(song)

	def insert(self, position, new_song):
		"""
		Insert a new song into the playlist at a specific position.
		"""

		if not isinstance(new_song, Song):
			#Not given a song reference, raise an error
			raise ValidationError("Not given a song reference to insert.")
			
		self.songs.add(new_song)

		self.song_list.insert(position, new_song.id)

		self._populate_songs()

	def append(self, new_song):
		"""
		Add a new song to the end of the playlist.
		"""
		if not isinstance(new_song, Song):
			#Not given a song reference, raise an error
			raise ValidationError("Not given a song reference to insert.")

		self.songs.add(new_song)

		self.song_list.append(new_song.id)

		self._populate_songs()

	def move(self, original_position, new_position):
		"""
		Move a song from one position to another
		"""
		if original_position == new_position:
			return

		song_id = self.song_list[original_position]

		#This is actually a bit more complicated than it first appears, since the index we're moving to may actually change
		#when we remove an item.
		if new_position < original_position:
			del self.song_list[original_position]
			self.song_list.insert(new_position, song_id)

		else:
			del self.song_list[original_position]
			self.song_list.insert(new_position - 1, song_id) #Account for the list indices shifting down.

		self._populate_songs()

	def remove(self, position):
		if position > len(self.song_list):
			return False

		del self.song_list[position]

		self._populate_songs()

	def export(self, playlist_type = "m3u"):
		"""
		Export this internal playlist to a file format.
		Supported formats:
			-pls
			-m3u
		Return value is a string containing the playlist -
		you can write it to file as you deem necessary.
		"""
		#Default m3u playlist type, support others as I build them.
		playlist_string = ""

		if playlist_type == "pls":
			#Playlist header
			playlist_string += "[playlist]"

			#Playlist body
			for index, song_id in enumerate(self.song_list):
				song = self.songs.get(id = song_id)

				playlist_string += "File" + str(index + 1) + "=" + song.url + "\n"
				playlist_string += "Title" + str(index + 1) + "=" + song.title + "\n"
				playlist_string += "Length" + str(index + 1) + "=" + str(song.duration) + "\n"

			#Playlist footer
			playlist_string += "NumberOfEntries=" + str(len(self.song_list))
			playlist_string += "Version=2"

		else:
			#Export m3u, default option if nothing else is recognized

			#Playlist header
			playlist_string += "#EXTM3U" + "\n"

			#Playlist body
			for song_id in self.song_list:
				song = self.songs.get(id = song_id)

				playlist_string += "#EXTINF:" + str(song.duration) + "," + song.artist + " - " + song.title + "\n"
				playlist_string += song.url + "\n\n"

			#Playlist footer

		return playlist_string

	def _import(self, playlist_string = None):
		"""
		Import and convert a playlist into native DB format.
		This function will return true if the playlist format was recognized, false otherwise.
		It will return true even if there are errors processing individual songs in the playlist.
		As a side note - the _import() name is used since python doesn't let
		you name a function import().
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
