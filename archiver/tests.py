"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

class FilesystemScanTest(TestCase):
	def test_filesystem_scan(self):
		"Tests that we can scan a filesystem correctly."
		import os
		from archiver.archive import Archive
		from Melodia.settings import PROJECT_FOLDER

		TEST_DATA_FOLDER = os.path.join(PROJECT_FOLDER, "test_data")
		new_archive      = Archive(root_folder = TEST_DATA_FOLDER)

		#We must save the archive before we can start adding songs to it
		new_archive.save()

		new_archive.quick_scan()

		new_archive.save()

class ScanTest(TestCase):
	def test_archive_scan(self):
		"Tests that we can scan an archive correctly."
		import os
		from archiver.archive import Archive
		from Melodia.settings import PROJECT_FOLDER

		TEST_DATA_FOLDER = os.path.join(PROJECT_FOLDER, "test_data")
		new_archive      = Archive(root_folder = TEST_DATA_FOLDER)

		#We must save the archive before we can start adding songs to it
		new_archive.save()
		new_archive.scan()
		new_archive.save()

class DeepScanTest(TestCase):
	def test_archive_deep_scan(self):
		"Tests that we can deep scan an archive correctly. This is currently broken, as EchoNest support does not exist."
		import os
		from archiver.archive import Archive
		from Melodia.settings import PROJECT_FOLDER

		TEST_DATA_FOLDER = os.path.join(PROJECT_FOLDER, "test_data")
		new_archive      = Archive(root_folder = TEST_DATA_FOLDER)

		#We must save the archive before we can start adding songs to it
		new_archive.save()
		new_archive.deep_scan()
		new_archive.save()

class PlaylistExportTest(TestCase):
	def test_playlist_export(self):
		"Tests that we can export a playlist."
		from archiver.archive import Archive
		from archiver.playlist import Playlist

		#----------------------------------------------------------------------------
		#- Re-using code from the scan to set up our archive.
		import os
		from archiver.archive import Archive
		from Melodia.settings import PROJECT_FOLDER

		TEST_DATA_FOLDER = os.path.join(PROJECT_FOLDER, "test_data")
		new_archive      = Archive(root_folder = TEST_DATA_FOLDER)

		#We must save the archive before we can start adding songs to it
		new_archive.save()
		new_archive.scan()
		new_archive.save()
		#----------------------------------------------------------------------------

		#Resume playlist testing code
		a_playlist = Playlist()
		a_playlist.name = "Testing..."
		a_playlist.save()

		for song in new_archive.songs.all():
			a_playlist.append(song)

		a_playlist.save()

		playlist_string = a_playlist.export()
