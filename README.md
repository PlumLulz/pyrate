# pyrate
https://mixunit.com album downloader.

Usage: python3 pyrate.py -url https://www.mixunit.com/p/1239095-gray-grey-suicideboys-2017 \
Usage: python3 pyrate.py -search "Project Pat" -l 10

# Update 3.0
- Added gevent to use multiple threads when downloading album tracks. This greatly improved download speeds as seen in the table below.
- Updated search function to clear previous results before the new results are displayed. This helps keep the console clear when going through search results.


| Albums Downloaded | Time with gevent | Time without gevent |
| --- | --- | --- |
| database1\ sadsadasd | 2GB | 3m:19s |
