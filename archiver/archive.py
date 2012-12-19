from django.db import models

from song import Song

"""
This is the archive model for the archiving backend of Melodia.
It's purpose is to control the high-level functionality of managing
multiple archives of music. It is different from a playlist both conceptually
and practically - an archive describes a group of files, while a playlist
describes a group of songs.
In this way, you back up archives of music - you don't back up the songs in a
playlist. Additionally, you may want to re-organize your music to use a
cleaner directory structure - a playlist doesn't care about this.
Note that archives are different from collections:
		-Archives are physical organizations of songs. These are used in the backend.
		-Collections are logical organizations of songs. These are intended to be used
			on the frontend.
	The difference is intended to separate the difference between logical and physical
	operations. For example, you don't need to re-organize the directory structure of
	a collection of songs. However, you may want to prevent kids from accessing explicit
	songs even if they are part of the same archive folder as clean songs.
"""

class Archive (models.Model):

	"""
	The archive model itself, and all functions used to interact with it.
	The archive is built up from a grouping of songs, and the functions
	that are used to interact with many songs at a single time. The archive
	for example allows you to re-organize a specific set of music files into
	a cleaner directory structure.
	The archive is given a folder to use as its root directory - it finds all
	music files under there, and takes control of them from there.
	"""

	name        = models.CharField(max_length  = 64)

	#Note that we're not using FilePathField since this is actually a folder
	root_folder = models.CharField(max_length  = 255)

	#And a reference to the songs in this archive
	songs       = models.ManyToManyField(Song)

	#Backup settings
	backup_location  = models.CharField(max_length = 255)
	backup_frequency = models.IntegerField()
	last_backup      = models.DateTimeField()

	def _scan_filesystem(self, progress_callback = lambda x: None):
		"Scan the archive's root filesystem and add any new songs"
		#This method is implemented since the other scan methods all need to use the same code
		#DRY FTW
		import re, os
		from django.core.exceptions import ObjectDoesNotExist
		from Melodia.melodia_settings import SUPPORTED_AUDIO_EXTENSIONS
		from Melodia.melodia_settings import HASH_FUNCTION as hash

		_regex = '|'.join(( '.*' + ext + '$' for ext in SUPPORTED_AUDIO_EXTENSIONS))
		regex  = re.compile(_regex, re.IGNORECASE)

		for dirname, dirnames, filenames in os.walk(self.root_folder):
			#For each filename
			for filename in filenames:
				#If the filename is a supported audio extension
				if re.match(regex, filename):
					#Make sure that `filename` is in the database
					try:
						self.songs.get(url = filename)

					except ObjectDoesNotExist, e:
						#Song needs to be added to database

						full_url = os.path.join(dirname, filename)
						new_song = Song(url = full_url)
						new_song.populate_metadata()
						new_song.save()
						self.songs.add(new_song)

	def quick_scan(self):
		"Scan this archive's root folder and make sure that	all songs are in the database."

		from os.path import isfile

		#Validate existing database results
		for song in self.songs.all():
			if not isfile(song.url):
				song.delete()

		#Scan the root folder, and find if we need to add any new songs
		self._scan_filesystem()

	def scan(self):
		"Scan this archive's root folder and make sure any local metadata are correct."
		#Overload the regular hash function with whatever Melodia as a whole is using
		from Melodia.melodia_settings import HASH_FUNCTION as hash
		import os.path

		for song in self.songs.all():

			if not os.path.isfile(song.song_url):
				song.delete()
				continue

			#The song exists, check that the hash is the same
			db_hash = song.file_hash
			
			f         = open(song_url)
			file_hash = hash(f.read())

			if file_hash != db_hash:
				#Something about the song has changed, rescan the metadata
				song.populate_metadata()

		#Make sure to add any new songs as well
		self._scan_filesystem()


	def deep_scan(self):
		"Scan this archive's root folder and make sure that	all songs are in the database, and use EchoNest to update metadata as necessary"

		#Overload the regular hash function with whatever Melodia as a whole is using
		from Melodia.melodia_settings import HASH_FUNCTION as hash
		import os.path

		for song in self.songs.all():

			if not os.path.isfile(song.song_url):
				song.delete()
				continue

			#The song exists, check that the hash is the same
			db_hash = song.file_hash
			
			f         = open(song_url)
			file_hash = hash(f.read())

			if file_hash != db_hash:
				#Something about the song has changed, rescan the metadata
				song.populate_metadata(use_echonest = True)

		#Make sure to add any new songs as well
		self._scan_filesystem()

	def _needs_backup(self):
		"Check if the current archive is due for a backup"
		import datetime

		prev_backup_time = self.last_backup
		current_time     = datetime.datetime.now()

		delta = current_time - prev_backup_time
		if delta > datetime.timedelta(seconds = self.backup_frequency):
			return True
		else:
			return False

	def run_backup(self, force_backup = False):
		"Backup the current archive"
		if force_backup or self._needs_backup():
			import subprocess
			subprocess.call(['rsync', '-av', self.root_folder, self.backup_location])
