# A word of caution! 
When I uploaded the software I only tested the eyed3 part with a few select files. After testing bigger batches, I've come to the conclusion that not all mp3 files are equal, and in fact the current implementation barely seems to work with the bigger part of my collection. If you still want to use this script, I **strongly** suggest you use the --no-rename function, so as to not lose information for files with unsuitable meta tags. To be fair, renaming the files to only the song name was a naive idea on my part to begin with, since it's perfectly possible for many files to share the same name. 
I'd also suggest adding try-except blocks to the code that handles meta tags in parsefiles.py, since the code will cease execution if it encounters any unsuitable file.

## Overview
If you don't rely on streaming services to listen to music then chances are you (much like me) have an unmanageable amount of uncategorised mp3 files in your devices.  
This project aims to make these kind of collections more application friendly by automatically filling out the most relevant metadata tags: Song title, artist name, album name, and album art.  
This is done in four steps, which can be done independently:
* Gathering and displaying all artist and album names. Useful to check for normalised capitalisation, punctuation, etc.
* Download images for all found artists and albums
* Add all downloaded images to the metadata
* Change the song title, artist name, and album name metadata

### User guide
This project uses `eyed3` to interact with mp3 metadata, and both `selenium` and `chromedriver_autoinstaller` to handle browser transactions, so be sure to have these packages installed and up to date.  
Execute `musicbuddy.pi` with the following options:

    Unless actions are specified, the script will perform all actions in sequence in the current directory
	Help:
	-h, --help            Show this message, then cease execution
	Actions:
	-l, --list            List found artists and albums
	-d, --download        Download images based on found artist and album names
	-a, --art             Fix the Album Art tag
	-m, --meta            Fix the Song Title, Artist, Album Name tags, and filename
	Directories:
	-i [directory]        Where to look for mp3 files
	-t [directory]        Where the images will be downloaded
	Options:
	--overwrite           Download images for all artists without checking if there's already viable ones
	--no-artist           Don't give default artist names to songs without artists
	--default [name]      Change the default artist name for songs without an artist
		              By default it's "Misc. Artist"
	--no-album            If no album name is specified, the album name field will 
	                      remain empty instead of being filled with the artist name by default
	--extra [name]        Add text to queries with no album name to get more suitable results 
	                      e.g. "latest album" or "live concert"
	-r, --no-remove       Don't delete downloaded images after using them
	--no-rename           Don't rename files after changing their metadata
	--keyword [name]      Parse filename for keywords to add to album name, e.g. "OST", "Live concert"  
                          Can be used multiple times to look for different key phrases
		
The script will work if files are formatted like this: [Artist - ]Song name[#Album].mp3  
If you want to use a different nomenclature then change the function `split_filename()` in `parsefiles.py`  
Artist and album name are optional and will be filled with default values if not specified.

Images are downloaded by opening a google chrome browser and searching the artist and album names in google images. If you want to change this, then take a look in `autoimgloader.py`. Using a different browser should be easy enough but using a different search engine requires some html and css knowledge.

I recommend carefully studying the options before doing anything. The default behaviour of this script makes a lot of assumptions which may yield  undesired results. These include:  
- Adding irrelevant tags to your files. By default, all files without an explicit album name have the artist's name added as an album, and all files without an explicit artist name get "Misc. Artist" added as the artist and possibly the album name.
- Creating any number of images in the current directory without erasing them afterwards.
- Renaming all found .mp3 files from "Artist - Song Name#Album.mp3" to "Song Name.mp3"
