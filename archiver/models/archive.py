"""
This is the Archive model for the backend of Melodia. It's functionality is to
provide a grouping of songs based on where they are located in the filesystem.
It controls the high-level functionality of managing multiple archives
of music - basically, multiple filesystem folders holding your music.
"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

import datetime
import re, os
from itertools import ifilter

from Melodia.melodia_settings import SUPPORTED_AUDIO_EXTENSIONS
from Melodia.melodia_settings import HASH_FUNCTION as hash

class Archive (models.Model):
    """
    .. data:: name

       String human-readable name of this archive -- ex. ``Steve's Music``

    .. data:: root_folder

       String containing the root folder of this archive. Should not be
       modified once the archive has been created.

    .. data:: backup_location

       String for the rsync-readable location that this archive should
       be backed up to. Can be modified if you need to change the location.

    .. data:: backup_frequency

       Integer time in minutes that should be between backups of this archive.
       This should not be blank, if you want to disable backups, set the
       location to being blank.

    .. data:: last_backup

       DateTime object that records when the last **successful** backup was run.
       Don't touch this.
    """

    name = models.CharField(max_length = 64)

    #Note that we're not using FilePathField since this is actually a folder
    root_folder = models.CharField(max_length = 512)

    #We've removed the reference to "songs" - instead define it as a ForeignKey,
    #and do lookups via song_set

    #Backup settings
    backup_location  = models.CharField(max_length = 255, default = None, null = True)
    backup_frequency = models.IntegerField(default = 10800) #1 week in minutes
    last_backup      = models.DateTimeField(default = datetime.datetime.now) #Note that this by default will be the time the archive was instantiated

    class Meta:
        app_label = 'archiver'

    def _scan_filesystem(self):
        """
        Scan the archive's root filesystem and add any new songs without adding
        metadata, delete songs that exist no more.
        .. todo:: 
           
           This should be fixed so that we don't drop all songs and re-add
           them. That's just terrible design.
        """
        #This method is implemented since the other scan methods all need to
        #use the same code. DRY FTW
        
        _supported_extns_regex = '|'.join(( '.*' + ext + '$' for ext
                                            in SUPPORTED_AUDIO_EXTENSIONS))
        regex  = re.compile(_supported_extns_regex, re.IGNORECASE)

        #It's hackish, but far fewer transactions to delete everything first,
        #and add it all back. If we get interrupted, just re-run it.
        song_set.all().delete()

        #For each filename that is supported
        for filename in ifilter(lambda filename: re.match(regex, filename), filenames):
            rel_url = os.path.join(dirname, filename)
            full_url = os.path.abspath(rel_url)
            new_song = Song(url = full_url)
            new_song.save()
            song_set.add(new_song)

    def _update_song_metadata(self, progress_callback = lambda x, y: None):
        """
        Scan every song in this archive (database only) and make sure all
        songs are correct. The progress_callback function is called with the
        current song being operated on first, and the total songs second.

        :param progess_callback: Function called to give progress. First
        argument is an integer for the song currently in progress, second
        argument is the total number of songs to be operated on.
        """
        total_songs  = song_set.count()

        for index, song in enumerate(song_set.all()):
            song.populate_metadata()
            song.save()
            progress_callback(index + 1, total_songs)

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
        """
        Scan this archive's root folder, add or remove songs from the DB
        as necessary.
        """
        self._scan_filesystem()

    def scan(self):
        """
        Like :func:`quick_scan` but makes sure all metadata is current.
        """
        #This is a longer scan - validate whether songs should exist, and use local data to update
        #the database

        self._scan_filesystem()
        self._update_song_metadata()

    def run_backup(self, force_backup = False):
        """
        Backup the current archive

        :param force_backup: Boolean value, if `True` will ensure backup runs.
        """
        if force_backup or self._needs_backup():
            import subprocess
            subprocess.call(['rsync', '-av', self.root_folder, self.backup_location])

    def reorganize(self, format_string,
                    progress_function = lambda w, x, y, z: None,
                    dry_run = False):
        """
        Reorganize a music archive using a given `format_string`. Recognized
        escape characters are below:

        .. table::

           ==========   ==============
           Character:   Replaced with:
           ==========   ==============
           %a           Artist Name
           %A           Album Name
           %d           Disc Number
           %e           Number of discs
           %f           Current Filename (with extension)
           %g           Current Filename (no extension)
           %n           Track Number
           %o           Number of tracks on disc
           %y           Album year
           ==========   ==============

        All re-organization takes place relative to the archive's
        :data:`root_folder`.

        :param format_string: String describing how each song should be re-organized
        :param progress_function: Optional function to get current progress - see notes below.
        :param dry_run: Boolean, if `True` will do everything except move files

        The progress_function is called with the current song number as its first argument, total songs as its second,
        current song URL as the third argument, and new URL as the fourth.
        """
        import os, shutil, errno

        total_songs = song_set.count()

        for index, song in enumerate(song_set.all()):
            _current_filename              = os.path.basename(song.url)
            _current_filename_no_extension = os.path.splitext(_current_filename)[0]

            _release_year = song.release_date.year

            new_location = format_string.replace("%a", song.artist)\
                                        .replace("%A", song.album)\
                                        .replace("%d", str(song.disc_number))\
                                        .replace("%e", str(song.disc_total))\
                                        .replace("%f", _current_filename)\
                                        .replace("%g", _current_filename_no_extension)\
                                        .replace("%n", str(song.track_number))\
                                        .replace("%o", str(song.track_total))\
                                        .replace("%y", str(_release_year))

            new_url = os.path.join(self.root_folder, new_location)

            progress_function(index + 1, total_songs, song.url, new_url)

            if not dry_run:
                new_folder = os.path.dirname(new_url)
                try:
                    #`mkdir -p` functionality
                    if not os.path.isdir(new_folder):
                        os.makedirs(new_folder)

                    #Safely copy the file - don't 'move' it, but do a full 'copy' 'rm'
                    #This way if the process is ever interrupted, we have an unaltered copy
                    #of the file.
                    shutil.copyfile(song.url, new_url)
                    shutil.copystat(song.url, new_url)

                    #Notify the database about the new URL
                    old_url  = song.url
                    song.url = new_url
                    song.save()

                    #Actually remove the file since all references to the original location have been removed
                    os.remove(old_url)

                except OSError as exc:
                    if exc.errno == errno.EEXIST and os.path.isdir(new_folder):
                        #This is safe to skip - makedirs() is complaining about a folder already existing
                        pass
                    else: raise

                except IOError as exc:
                    #shutil error - likely that folders weren't specified correctly raise
					raise
