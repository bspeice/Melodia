from django.db import models
import datetime, time
import feedparser

from archive import Archive


"""
The "Feed" model describes a podcast feed using any of RSS, Atom, etc.
Backend handling is processed by 'feedparser', we just download all the podcast files,
control how many are stored, etc. The feed is intended to belong to an archive - 
this way the feed is backed up automatically (and we don't have the podcast spewing
files everywhere).
It is important to note - the "max_episodes" field regulates how many episodes are
stored and backed up. A value < 1 indicates storing all episodes.
"""

_audio_type_mime_types = [
		u'audio/mpeg'
		]

_audio_type_mime_types_string = "\n".join(_audio_type_mime_types)

class Feed(models.Model):
	class Meta:
		app_label = 'archiver'

	url = models.URLField()
	name = models.CharField(max_length = 64)
	max_episodes = models.IntegerField(default = 0) # Default store everything
	current_episodes = models.IntegerField(default = 0)
	last_episode = models.DateTimeField(default = datetime.datetime(1970, 1, 1))
	parent_archive = models.ForeignKey(Archive)

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
		Update the podcast with episodes from the server copy. If dry_run, don't actually download episodes,
		but show what changes would have been made (implies forbid_delete). If forbid_delete, download all new
		episodes, ignoring the max_episodes count.
		"""
		pass
