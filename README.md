Melodia
=====

What is it?
-----------
Melodia is a Music Manager framework to manage a music archive. This includes:
*	Music archiving -
	*	Backup and restore
	*	Tagging completion and maintenance
	*	Music archive re-organization

*	Music player -
	*	Web music player
	*	Playlist management
	*	Playlist download - download the songs in a playlist

*	Other features to come as deemed necessary. Some ideas:
	*	Local music player
	*	RSS support and archiving

The name comes from the Portugese for "melody." Plus, I just needed a catchy name. Python Music Manager is just very non-descript.

Why do this?
------------
Melodia was created for a number of different reasons. I needed a project to keep myself busy, and wanted to learn Django. Beyond that, I've maintained a personal music collection on a hard drive, and have had a sufficiently hard time trying to keep it organized, keep it centralized, ensure tags were all filled out, etc. Additionally, trying to create subsets of that archive (I.e. the songs that I wanted to put on my phone) has been challenging to say the least.

On this note then, I wanted to create a music system that could be used in place of a standard local program. This way, I can have one copy of my music across the network, and use it everywhere else.

Why not MPD? XMMS2? Other server music players?
-----------------------------------------------
Good question. Besides just wanting to learn Django, there are some good reasons to create Melodia:

*	Music archiving isn't very good. I haven't found software that I can use to manage the archive.
*	Making one library available to multiple network locations is problematic. You can use something like IceCast with XMMS2, but that lets only one person control the song choice. I needed something a decent bit more flexible.
*	Managing multiple archives is problematic. I need to create a subset of songs to play on a different device that may not have as much space, etc.
*	Create a web-enabled music player is also important. XMMS2 only allows you to work through IceCast, and enabling something like a socket to XMMS2 concerns me. Just doesn't seem very secure.
*	Using a server architecture isn't the only thing happening. If I just wanted a local music server, I'd use MPD. I want a full music player available, frontend, everything.

Questions? Comments? Concerns?
------------------------------
Let me know!
