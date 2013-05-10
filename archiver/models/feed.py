"""
The Feed model describes a podcast of anything that can be parsed by :mod:`feedparser`.
Most of the heavy lifting is done via :mod:`feedparser`, we just download the
podcast files.
"""

from django.db import models
import datetime, time
import feedparser

from archive import Archive

# What mime types should be downloaded from the podcast XML
_audio_type_mime_types = [
        u'audio/mpeg'
        ]

_audio_type_mime_types_string = "\n".join(_audio_type_mime_types)

class Feed(models.Model):
    """
    .. data:: url
       
       String representation of The URL from which the podcast
       file should be downloaded.

    .. data:: name
    
       Human-readable string for this podcast. This is set by the user, not by
       the XML podcast name. Is the name for the folder in which this podcast
       is stored.

    .. data:: max_episodes

       Integer for how many fields should be stored at a time. A value of ``0``
       (or ``< 0``) indicates that all episodes should be stored. A positive
       value controls how many episodes are stored at a time.

    .. data:: current_episodes

       Integer for how many episodes are currently stored locally. This will
       be deprecated, as it can be calculated.

    .. data:: last_episode
       
       DateTime object for the date of the most recent file downloaded. This
       should not be modified by anything outside this model.

    .. data:: parent_archive

       Reference to the :class:`Archive` this podcast belongs to. Informs the
       feed where it should store its files at.
    """

    url = models.URLField()
    name = models.CharField(max_length = 64)
    max_episodes = models.IntegerField(default = 0) # Default store everything
    current_episodes = models.IntegerField(default = 0)
    last_episode = models.DateTimeField(default = datetime.datetime(1970, 1, 1))
    parent_archive = models.ForeignKey(Archive)

    class Meta:
        app_label = 'archiver'

    def _get_episode_time(episode):
        """
        Get a datetime.datetime object of a podcast episode's published time.
        Expects a specific element from feed_object.entries.
        """
        t = time.mktime(episode.published_parsed)
        return datetime.datetime.fromtimestamp(t)

    def _calculate_new_episodes(feed_object):
        """
        Calculate how many new episodes there are of a podcast (and consequently
        how many we need to remove).
        """
        num_episodes = 0

        #feed_object.entries starts at the most recent
        for episode in feed_object.entries:
            if _get_episode_time(episode) > last_episode:
                num_episodes += 1

            #Don't set ourselves up to download any more than max_episodes
            if num_episodes > max_episodes and max_episodes > 0:
                return num_episodes

        return num_episodes

    def _download_podcast(feed_object, num_episodes = -1):
        """
        Update this podcast with episodes from the server copy. The feed_object is a reference to a
        feedparser object so we don't have to redownload a feed multiple times.
        """

        num_episodes = _calculate_new_episodes()

        #feedparser-specific way of building the list
        new_episodes = feed_object.entries[:num_episodes]

        for episode in new_episodes:
            episode_audio_links = [link for link in episodes['links']
                                            if link['type'] in _audio_type_mime_types_string]

            print episode_audio_links

                
    def sync_podcast(dry_run = False, forbid_delete = False):
        """
        Update the podcast with episodes from the server copy.

		:param dry_run: Calculate what would have been downloaded or deleted, but do not actually do either.
		:param forbid_delete: Run, and only download new episodes. Ignores the :data:`max_episodes` field for this podcast.

        """
        pass
