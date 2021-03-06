#!/usr/bin/env python3
'''
pythonhockey - a command-line tool written in Python3 to automate FNeulion
Copyright (C) 2015 pythonhockey

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

*** IMPORTANT JAVA NOTE: This script kills any running ***
*** Java instances when started. If this isn't what    ***
*** you want to happen, comment out line below the     ***
*** # Kill previous java instances comment             ***
***                                                    ***
*** More information available in README file          ***
'''

import re, sys, subprocess

try:
    import requests
except ImportError:
    if sys.platform == 'linux' or sys.platform == 'linux2':
        sys.stderr.write("You must install \'requests\' module. Go back to Terminal and type \'sudo pip3 install requests\'\n")
        sys.exit(1)
    elif sys.platform == 'darwin':
        sys.stderr.write("You must install \'requests\' module. Go back to Terminal and type \'pip3 install requests\'\n")
        sys.exit(1)

# Print schedule of active games
def activeGames():
    scheduleRE = re.compile(r'Game Thread: [\w\s]+at[\w\s\d\:]+ET')
    scheduleMO = scheduleRE.findall(subreddit.text)
    schedule1 = '\n'.join(scheduleMO)
    schedule = re.sub('Game Thread: ', '', schedule1)
    return schedule

# Request subreddit text
def subredditText():
    try:
        subreddit = requests.get('https://www.reddit.com/r/NHLStreams/')
        while subreddit.status_code != 200:
            subreddit = requests.get('https://www.reddit.com/r/NHLStreams/')
    except:
        pass
    return subreddit

# Regex of game thread url
def selectTeam(mascot):
    findLink = re.compile(r'/r/NHLStreams/comments/(\w)+/game_thread(\w)+%s(\w)+_et/' % mascot)
    mo1 = findLink.search(subreddit.text)
    if not mo1:
        print('This team is not currently playing.')
        sys.exit()
    else:
        endURL = mo1.group()
    return 'https://reddit.com' + endURL

# Search for 'Game ID for FNeulion: #########'

def gameIdForFneulion(): 
    findID = requests.get(gameThread)
    try:
        while findID.status_code!=200:
            findID = requests.get(gameThread)
    except:
        pass
    fneulion = re.compile(r'Game ID for FNeulion:\s?\d{9,}')
    fneulion_mo = fneulion.search(findID.text)
    gameID = re.sub('Game ID for FNeulion: ', '', fneulion_mo.group())
    return gameID

## BEGIN PROGRAM ##

subreddit = subredditText()

if sys.argv[1].lower() == 'schedule':
    print(activeGames())
    sys.exit()
elif sys.argv[1].lower() == 'mapleleafs' or sys.argv[1].lower() == 'maple_leafs':
    mascot = 'leafs'
else:
    mascot = str(sys.argv[1].lower())
homeOrAway = None

# Bitrate 

if len(sys.argv) == 2:
    bitrate = None
elif sys.argv[2] not in ('800', '1600', '3000', '4500', '5000'):
    print('You did not select a valid bitrate. Valid bitrates are 800, 1600, 3000, 4500, and 5000.\n**Attempting to start stream at default quality.**')
    bitrate = None
else:
    bitrate = str(sys.argv[2])

# Kill previous java instances

subprocess.call(['sudo','pkill','java'], stdout=None, stderr=None)

# Open NHLstream subreddit, search for team name (mascot), open link

beforeAt = re.compile(r'Game Thread: %s at' % mascot.title())
beforeAtMo = beforeAt.search(subreddit.text)
if beforeAtMo == None:
    homeOrAway = 'home'
else:
    homeOrAway = 'away'

gameThread = selectTeam(mascot)

gameIdString = gameIdForFneulion()
print(gameIdString)

# Launch FNeulion

streamUrl = subprocess.Popen(['sudo','java','-jar','FuckNeulionV2.3.jar',gameIdString,homeOrAway], stdout=subprocess.PIPE, stderr=None)

# Grab URL from standard output of FNeulion stream 
i = 0
while i < 2:
    url = streamUrl.stdout.readline()
    i += 1
url = url.decode(encoding='UTF-8').strip()
if len(sys.argv) == 2 or sys.argv[2] not in ('800', '1600', '3000', '4500', '5000'):
    pass
else:
    url = url.replace('ipad', bitrate)

if sys.platform == 'linux' or sys.platform == 'linux2':
    vlc = subprocess.Popen(['/usr/bin/vlc',url], stdout=None, stderr=None)
elif sys.platform == 'darwin':
    vlc = subprocess.Popen(['open','-a','VLC',url], stdout=None, stderr=None)
