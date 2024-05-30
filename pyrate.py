##
# pyrate.py
# http://mixunit.com album downloader
# @author Plum
# @version 3.0
# Usage: python3 pyrate.py -url https://www.mixunit.com/p/1239095-gray-grey-suicideboys-2017
# Usage: python3 pyrate.py -search lol
##

import os
import bs4
import sys
import eyed3
import gevent
import argparse
from gevent import monkey
from gevent.pool import Pool

# Monkey patch before importing requests to avoid warnings
monkey.patch_all()

import requests


# Create pool for workers
# Edit at your own risk. Can cause laginess on computer if there are too many workers
pool = Pool(50)

# Parse all album details and tracklist from page source
def album_details(soup, tracknums):
	try:
		details = soup.find("div", {"class": "details"}).h1.text.split("|")
	except AttributeError:
		return False
	album = details[0].strip()
	artist = details[1].strip()
	tracks = soup.find("ul", {"class": "tracks"})
	albumid = tracks['data-uuid']
	albumart =  soup.find("img", {"class": "mixtape-cover"})['src']

	# Get tracklist information
	tracklist = {}
	for li in tracks.find_all('li'):
		trackid = li['data-track']
		track = li.h4.text
		tracknum = li.find("span", {"class": "track-no"}).text
		if tracknums:
			if tracknum in tracknums:
				tracklist.update({trackid: track})
		else:
			tracklist.update({trackid: track})

	album_info = {
		"album": album,
		"artist": artist,
		"albumid": albumid,
		"albumart": albumart,
		"tracklist": tracklist
	}
	return album_info

# Track download worker
def worker(dl_url, trackid, trackname, dirname):
		get = requests.get(dl_url+trackid)
		trackpath = dirname+"/"+trackname+".mp3"
		with open(trackpath, "wb+") as file:
			file.write(get.content)
		eyed = eyed3.load(trackpath)
		eyed.tag.images.set(3, open(dirname+"/album_art.jpg",'rb').read(), 'image/jpeg')
		eyed.tag.save()
		print("Downloaded track: %s" % (trackname))

# Download each track and album art
def download_album(dirname, albumid, tracks):
	# Create dirctory and download album art to dir
	try:
		os.mkdir(dirname)
	except OSError as e:
		print ("Failed to create directory %s" % dirname)
		print(e)
		exit()
	else:
		print ("Created directory '%s'" % dirname)
		getart = requests.get(details['albumart'])
		with open(dirname+"/album_art.jpg", "wb+") as image:
			image.write(getart.content)
		print("Downloaded album art")

    # Download each track file
	dl_url = "https://www.mixunit.com/p/%s/track/" % (albumid)
	jobs = []
	for track in tracks.items():
		trackid = track[0]
		trackname = track[1].replace("/", "\\")
		jobs.append(pool.spawn(worker, dl_url, trackid, trackname, dirname))
	pool.join()


# Search for music
def search(keyword, limit, offset):
	surl = "https://www.mixunit.com/search/get-results?keywords=%s&limit=%s&offset=%s&category=a4ylz5pzzkimg37n&searchWithinCategory=true" % (requests.utils.quote(keyword), limit, offset)
	get = requests.get(surl).json()
	status = get['status']
	if status == 200:
		total = get['total']
		soup = bs4.BeautifulSoup(get['results'], features="html.parser")
		a = soup.find_all("a", {"class": "item-thumbnail open-mixtape"})
		results = []

		print("\n%s Total results for '%s'" % (total, keyword))
		if offset == 0:
			print("Showing results from %s - %s\n" % (offset, limit))
		else:
			print("Showing results from %s - %s\n" % (offset, int(offset)+int(limit)))
		for aid, row in enumerate(a):
			title = row['data-product-page-title'][:-15]
			url = row['href']
			results.append([url, title])
			print("ID: %s Title: %s" % (aid, title))
		inp = input("\nHit enter for next page, type 'none' to cancel, 'all' to download results displayed, or IDs separated by commas to download: ")
		if inp.lower() == "none":
			pass
		elif inp.lower() == "all":
			for aurl in results:
				get = requests.get(aurl[0]).text
				global details
				details = album_details(bs4.BeautifulSoup(get, features="html.parser"), tracknums)

				# Download album after details are obtained
				if details:
					print("Obtained '%s' details" % (details['album']))
					download_album(details['artist']+" - "+details['album'], details['albumid'], details['tracklist'])
				else:
					print("Failed to get album details for: %s" % (aurl[1]))
		elif inp.lower() == "":
			if offset == 0:
				offset = limit
				if int(offset) > int(total.replace(",", "")):
					offset = 0
					print("\033[%sF\033[J" % (int(len(a))+8), end="")
					print("No more results to display, refreshing last page.")
					search(keyword, limit, offset)
				else:
					print("\033[%sF\033[J" % (int(len(a))+6), end="")
					search(keyword, limit, offset)
			else:
				offset = int(offset) + int(limit)
				if int(offset) > int(total.replace(",", "")):
					print("\033[%sF\033[J" % (int(len(a))+8), end="")
					print("\nNo more results to display, refeshing last page.")
					search(keyword, limit, int(offset)-int(limit))
				else:
					print("\033[%sF\033[J" % (int(len(a))+6), end="")
					search(keyword, limit, offset)
		else:
			inp = inp.split(",")
			for aid in inp:
				if int(aid) < int(total.replace(",", "")):
					get = requests.get(results[int(aid)][0]).text
					details = album_details(bs4.BeautifulSoup(get, features="html.parser"), tracknums)

					# Download album after details are obtained
					if details:
						print("Obtained '%s' details" % (details['album']))
						download_album(details['artist']+" - "+details['album'], details['albumid'], details['tracklist'])
					else:
						print("Failed to get album details for: %s" % (results[aid][1]))
	elif status == 404:
		print("No results found.")

# Print header
print ("""
     ___
     \_/
      |._
      |'."-._.-""--.-"-.__.-'/ 
      |  \       .-.        (         _____                 _       
      |   |     (@.@)        )       |  __ \               | |      
      |   |   '=.|m|.='     /        | |__) |   _ _ __ __ _| |_ ___ 
      |  /    .='`"``=.    /         |  ___/ | | | '__/ _` | __/ _ \\
      |.'                 (          | |   | |_| | | | (_| | ||  __/
      |.-"-.__.-""-.__.-"-.)         |_|    \__, |_|  \__,_|\__\___|
      |                                      __/ |                  
      |                                     |___/ 
      |
      |
""")

# Parse arguments
parser = argparse.ArgumentParser(description='http://mixunit.com album downloader')
g1 = parser.add_mutually_exclusive_group(required=True)
g1.add_argument('-url', help='Enter URL of mixunit.com album to download.')
g1.add_argument('-search', help='Artist or album to search for.')
parser.add_argument('-tracks', help='List of tracks to download separated by commas. Ex: 2,3,10,11')
parser.add_argument('-limit', help='Value to limit search results by.', default=60)
args = parser.parse_args()
url = args.url
if args.tracks:
	tracknums = args.tracks.split(",")
else:
	tracknums = None

if args.url:
	# Get album details and tracklist
	get = requests.get(url).text
	details = album_details(bs4.BeautifulSoup(get, features="html.parser"), tracknums)

	# Download album after details are obtained
	if details:
		print("Obtained '%s' details" % (details['album']))
		download_album(details['artist']+" - "+details['album'], details['albumid'], details['tracklist'])
	else:
		print("Failed to get album details. Check to make sure URL is correct.")
elif args.search:
	# In order to use ANSI escape codes on Windows they must be activated first.
	# The easiest way that I have found is to simply run the color command first
	if sys.platform == 'win32':
		os.system("color")
	search(args.search, args.limit, 0)
