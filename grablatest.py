import bs4
import subprocess
import requests
import time
import os
import re

link = 'https://play.rtl.lu/shows/lb/journal/episodes'
links = []
folder = '/mnt/Download/SERIES/RTL Journal/'

now = time.strftime("%Y-%m")
nowday = time.strftime("%d")
time = time.strftime("%H:%M")

print('Running script at ' + time )

# check if latest episode already exists in folder
filename =  folder  + 'journal' + nowday + now + '.ts'
if os.path.isfile(filename):
    print('File ' + filename + ' already exists, exiting')
    exit()
else:
    print('File ' + filename + ' does not exist, continuing')

# get content of web page
page = requests.get(link).text
soup = bs4.BeautifulSoup(page, features="html.parser")

for a in soup.find_all('a', href=True):
    links.append(a['href'])

lastepisode = "https://play.rtl.lu" + links[8]

# open website lastepisode
today = requests.get(lastepisode).text
soup = bs4.BeautifulSoup(today, features="html.parser")
m3u8 = soup.find('meta', property="og:video")
baseurl = m3u8.get("content", None).strip('playlist.m3u8')

# check if latest episode already uploaded
soup.find(text=re.compile('De Journal')) 
latestjournalday = soup.find(text=re.compile('De Journal')).strip("De Journal vum ").partition('.')[0]
if nowday == latestjournalday:
    print('Grabbing latest episode')
    pass
else:
    print('Latest episode not yet uploaded')
    exit()

# get playlistfile and chose the 1080p chunklist
r = requests.get(m3u8.get("content", None))
m3u8hdurl = r.text.split('\n')[13]

# todo: program fstab on raspberry
subprocess.call(['sudo','ffmpeg', '-y', '-i', baseurl + m3u8hdurl, '-codec','copy', folder + 'journal' + nowday + now + '.ts'])

