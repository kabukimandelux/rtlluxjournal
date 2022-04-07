import bs4
import subprocess
import requests
import time
import os
import re
import json
import telegram


# To use the script change the folder to whatever suits you or output in same directory. I run the script on a pi using crontab.

link = 'https://play.rtl.lu/shows/lb/journal/episodes'
links = []
folder = '/mnt/Download/SERIES/RTL Journal/'

now = time.strftime("%Y-%m-%d")
nowday = time.strftime("%d")

def log(text):
    nowtime = time.strftime("%Y-%m-%d %H:%M:%S")
    print( nowtime + ': ' + text)

def notify_ending(message):
    with open('keys.json', 'r') as keys_file:
        k = json.load(keys_file)
        token = k['token']
        chat_id = k['chat_id']    
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=message)
    
# check if latest episode already exists in folder
filename =  folder  + 'journal' + now + '.ts'
if os.path.isfile(filename):
    log( 'File ' + filename + ' already exists, exiting' )
    exit()
else:
    log( filename + ' does not exist, continuing')

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
    log('Grabbing latest episode')
    pass
else:
    log('Daily episode not yet uploaded')
    exit()

# get playlistfile and chose the 1080p chunklist
r = requests.get(m3u8.get("content", None))
m3u8hdurl = r.text.split('\n')[13]

# todo: program fstab on raspberry
subprocess.call(['sudo','ffmpeg', '-y', '-i', baseurl + m3u8hdurl, '-codec','copy', folder + 'journal' + now + '.ts'])

notify_ending('RTL Journal from day ' + now + ' uploaded to Plex')
log('Script finished')
