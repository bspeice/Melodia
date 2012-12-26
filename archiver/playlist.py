from django.db import models

from song import Song
from listfield import IntegerListField

"""
Playlist model
Each playlist is a high-level ordering of songs. That's really it...
"""

class Playlist (models.Model):
	"The Playlist class defines the playlist model and its operations"

	name       = models.CharField(max_length = 255)
	song_order = IntegerListField()

	#This is a bit of a backup field, since technically the song PK's are in
	#the song_order field. However, it might be useful to just get a reference
	#to the songs in this playlist. Additionally, it's kind of hackish to reference
	#the global Song manager, rather than something that is specific for this playlist.
	songs      = models.ManyToManyField(Song)

	def _populate_songs(self):
		"""Make sure that the 'songs' relation is up-to-date."""
		#This operation works by getting the ID's for all songs currently in the playlist,
		#calculates what we need to add, what we need to remove, and then does it.
		#As much work as is possible is done on the python side to avoid the DB
		current_song_ids     = [song.id for song in self.songs.all()]
		current_song_ids_set = set(current_song_ids)

		new_song_ids_set = set(song_order)

		remove_set = current_song_ids_set.difference(new_song_ids_set)
		add_set    = new_song_ids_set.difference(current_song_ids_set)

		for song_id in remove_set:
			song = self.songs.get(id = song_id)
			song.remove()

		for song_id in add_set:
			song = Song.objects.get(id = song_id) #Using the global Songs manager is unavoidable for this one
			self.songs.add(song)

	def insert(self, position, new_song):
		"""Insert a new song into the playlist at a specific position."""

		if not isinstance(new_song, Song):
			#Not given a song reference, raise an error
			raise ValidationError("Not given a song reference to insert.")
			
		self.songs.add(new_song)

		self.song_order.insert(position, new_song.id)

		_populate_songs()

	def append(self, new_song):
		"""Add a new song to the end of the playlist."""
		if not isinstance(new_song, Song):
			#Not given a song reference, raise an error
			raise ValidationError("Not given a song reference to insert.")

		self.songs.add(new_song)

		self.song_order.append(new_song.id)

	def move(self, original_position, new_position):
		"""Move a song from one position to another"""
		if original_position == new_position:
			return

		song_id = self.song_order[original_position]

		#This is actually a bit more complicated than it first appears, since the index we're moving to may actually change
		#when we remove an item.
		if new_position < original_position:
			del self.song_order[original_position]
			self.song_order.insert(new_position, song_id)

		else:
			del self.song_order[original_position]
			self.song_order.insert(new_position - 1, song_id) #Account for the list indices shifting down.

	def remove(self, position):
		if position > len(self.song_order):
			return False

		del self.song_order[position]

	def export(self, playlist_type = "m3u"):
		"""Export this internal playlist to a file format."""
		#Default m3u playlist type, support others as I build them.

		if playlist_type = "pls":
			pass

		else:
			#Export m3u, default option
