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

		new_archive._scan_filesystem()

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

class DeepScanTest(TestCase):
	def test_archive_deep_scan(self):
		"Tests that we can deep scan an archive correctly."
		import os
		from archiver.archive import Archive
		from Melodia.settings import PROJECT_FOLDER

		TEST_DATA_FOLDER = os.path.join(PROJECT_FOLDER, "test_data")
		new_archive      = Archive(root_folder = TEST_DATA_FOLDER)

		#We must save the archive before we can start adding songs to it
		new_archive.save()

		new_archive.deep_scan()
