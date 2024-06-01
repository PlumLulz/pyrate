# pyrate
https://mixunit.com album downloader.

Usage: python3 pyrate.py -url https://www.mixunit.com/p/1239095-gray-grey-suicideboys-2017 \
Usage: python3 pyrate.py -search "Project Pat" -l 10

# Update 3.0
- Added gevent to use multiple threads when downloading album tracks. This greatly improved download speeds as seen in the table below.
- Updated search function to clear previous results before the new results are displayed. This helps keep the console clear when going through search results.


| Albums Downloaded | Time with gevent | Time without gevent |
| --- | --- | --- |
| Project Pat - Street God #2<br/>Project Pat - Street God #3 | 0m43s | 2m:53s |
| 99 Ways To Die - Master P (1995)<br/>Game Face - Master P (2001)<br/>Ghetto Postage - Master P (2000) | 2m:13s | 6m:14s |
