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
"""

class Archive (models.Model):
	import datetime

	"""
	The archive model itself, and all functions used to interact with it.
	The archive is built up from a grouping of songs, and the functions
	that are used to interact with many songs at a single time. The archive
	for example allows you to re-organize a specific set of music files into
	a cleaner directory structure.
	The archive is given a folder to use as its root directory - it finds all
	music files under there, and takes control of them from there.
	"""

	name        = models.CharField(max_length = 64)

	#Note that we're not using FilePathField since this is actually a folder
	root_folder = models.CharField(max_length = 255)

	#And a reference to the songs in this archive
	songs       = models.ManyToManyField(Song)

	#Backup settings
	backup_location  = models.CharField(max_length = 255, default = "/dev/null")
	backup_frequency = models.IntegerField(default = 604800) #1 week in seconds
	last_backup      = models.DateTimeField(default = datetime.datetime.now()) #Note that this by default will be the time the archive was instantiated

	def _scan_filesystem(self):
		"Scan the archive's root filesystem and add any new songs without adding metadata, delete songs that exist no more"
		#This method is implemented since the other scan methods all need to use the same code
		#DRY FTW
		import re, os
		from django.core.exceptions import ObjectDoesNotExist
		from Melodia.melodia_settings import SUPPORTED_AUDIO_EXTENSIONS
		from Melodia.melodia_settings import HASH_FUNCTION as hash

		_regex = '|'.join(( '.*' + ext + '$' for ext in SUPPORTED_AUDIO_EXTENSIONS))
		regex  = re.compile(_regex, re.IGNORECASE)

		#Remove songs in the database if they exist no longer
		#	-Do this first since we don't need to re-check songs that were just added
		for song in self.songs.all():
			if not os.path.isfile(song.url):
				song.delete()
				continue

		#Add new songs
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
						new_song.save()
						self.songs.add(new_song)

	def _update_song_metadata(self, use_echonest = False, progress_callback = lambda x, y: None):
		"Scan every song in this archive (database only) and make sure all songs are correct"
		#This method operates only on the songs that are in the database - if you need to make
		#sure that new songs are added, use the _scan_filesystem() method in addition
		total_songs  = self.songs.count()
		current_song = 0

		for song in self.songs.all():
			current_song += 1
			song.populate_metadata(use_echonest = use_echonest)
			progress_callback(current_song, total_songs)

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

	def quick_scan(self):
		"Scan this archive's root folder and make sure that	all songs are in the database."
		#This is a quick scan - only validate whether or not songs should exist in the database

		self._scan_filesystem()

	def scan(self):
		"Scan this archive's root folder and make sure any local metadata are correct."
		#This is a longer scan - validate whether songs should exist, and use local data to update
		#the database

		self._scan_filesystem()
		self._update_song_metadata()

	def deep_scan(self):
		"Scan this archive's root folder and make sure that	all songs are in the database, and use EchoNest to update metadata as necessary"
		#This is a very long scan - validate whether songs should exist, and use Echonest to make sure
		#that metadata is as accurate as possible.
		self._scan_filesystem()
		self._update_song_metadata(use_echonest = True)

	
	def run_backup(self, force_backup = False):
		"Backup the current archive"
		if force_backup or self._needs_backup():
			import subprocess
			subprocess.call(['rsync', '-av', self.root_folder, self.backup_location])
