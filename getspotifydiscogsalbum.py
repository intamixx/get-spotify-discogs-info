#!/usr/bin/python3

try:
        import socket
        import sys
        import os
        import pycurl
        import getopt
        import json
        import re
        import time
        import json
        import requests
        #from urllib.parse import urlencode
        from subprocess import Popen, PIPE
        from io import BytesIO
        from io import StringIO
        from mutagen.id3 import ID3
        import locale
        from dialog import Dialog
        from mutagen.id3 import ID3, TALB, TXXX, TYER, _util, error
        from mutagen.mp3 import MP3

except ImportError as e:
        print ("\n%s is installed. Please install it before running this script." % (e))
        exit (1)

locale.setlocale(locale.LC_ALL, '')

def add_id3_info(file_name, album_info, album_info_bool: bool, custom_info, custom_info_bool: bool, year_info, year_info_bool: bool):
#def add_id3_info(file_name, album_info, custom_info, year_info):
#def add_id3_info(file_name, album_info, album_bool: bool=False, year_info, year_info_bool: bool=False):
    """
    Add album_art in .mp3's tags
    """
    print (file_name)
    print (album_info)
    print (album_info_bool)
    print (custom_info)
    print (custom_info_bool)
    print (year_info)
    print (year_info_bool)
#    sys.exit(0)

    try:
        stinfo = os.stat(file_name)
    except:
        print ("Problem performing a file stat")
        sys.exit(1)
    atime = int(stinfo.st_atime)
    print ("access time of %s: %s" % (file_name, atime))
    mtime = int(stinfo.st_mtime)
    print ("modified time of %s: %s" % (file_name, mtime))

    if album_info_bool == True:
        try:
            file = ID3(file_name)
            file.delall("TALB")
            file.save(v2_version=3)
        except:
            print ("Problem deleting TALB ID3 tags")
            sys.exit(1)

    if custom_info_bool == True:
        try:
            file = ID3(file_name)
            file.delall("TXXX")
            file.save(v2_version=3)
        except:
            print ("Problem deleting TXXX ID3 tags")
            sys.exit(1)

    if year_info_bool == True:
        try:
            file = ID3(file_name)
            file.delall("TYER")
            file.save(v2_version=3)
        except:
            print ("Problem deleting TYER ID3 tags")
            sys.exit(1)

    audio = MP3(file_name, ID3=ID3)

    try:
        audio.add_tags()
    except:
        #print ("Problem adding MP3 tags to file")
        pass

    if album_info_bool == True:
        audio.tags.add(
            TALB(
                encoding=3,  # UTF-8
                text=album_info,
            )
        )

    if custom_info_bool == True:
        audio.tags.add(
            TXXX(
                encoding=3,  # UTF-8
                text=custom_info,
            )
        )
    if year_info_bool == True:
        audio.tags.add(
            TYER(
                encoding=3,  # UTF-8
                text=year_info,
            )
        )

    audio.save(v2_version=3)

    time.sleep(1)

    print ("Resetting stat information...")
    try:
        os.utime(file_name,times=(atime, mtime))
        #os.utime(file_name,times=(1330712280, 1330712292))
    except:
        print ("Problem setting a file stat")
        sys.exit(1)

    return 0

def get_album_from_discogs(song_title):
        url =  'https://api.discogs.com/database/search?q={}&sort=want'.format(song_title)
        print (url)

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.TIMEOUT, 15)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, ['Content-Type: application/json','Accept-Charset: UTF-8', 'Authorization: Discogs token=CznRojaxbAbuOK'
])
        try:
                c.perform()
        except pycurl.error:
                errno, errstr = pycurl.error
                print ("An error occurred: ", errstr)
                sys.exit(2)
        song = buffer.getvalue()
        if not song:
                print ("No information retrieved from discogs")
                sys.exit(2)
        else:
                #song = song.replace('&', '\&').replace("'", "")
#                print (song)
                print ("hello")

        print('Status: %d' % c.getinfo(c.RESPONSE_CODE))
        print('Status: %f' % c.getinfo(c.TOTAL_TIME))
        if c.getinfo(c.RESPONSE_CODE) == 200:
            buffer.close()
            c.close()
            return (song)
        else:
            print ("error with discogs")
            buffer.close()
            c.close()
            sys.exit(1)

def get_token_from_spotify():
    #credentials
    CLIENT_ID = '9ff2e4c369'
    CLIENT_SECRET = 'a03cad6b'

    # Here is where the error was, json.dump removed
    request_body_token = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'redirect_uri': 'http://localhost:8000'
    }

    access_token_request = requests.post(url='https://accounts.spotify.com/api/token', data=request_body_token, timeout=15)
    print(access_token_request.status_code)
    access_token = access_token_request.json()['access_token']
    print (access_token)
    return (access_token)


def get_album_from_spotify(song_title, spotify_token):
        #url =  'https://api.discogs.com/database/search?q={}&sort=want'.format(song_title)
        url =  'https://api.spotify.com/v1/search?q={}&type=track,artist'.format(song_title)
        print (url)

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.TIMEOUT, 5)
        c.setopt(c.WRITEDATA, buffer)
        header = 'Content-Type: application/json','Accept-Charset: UTF-8', 'Authorization: Bearer {}'.format(spotify_token)
        print (header)
        print (spotify_token)
        #c.setopt(c.HTTPHEADER, ['Content-Type: application/json','Accept-Charset: UTF-8', 'Authorization: Bearer' spotify_token])
        c.setopt(c.HTTPHEADER, header)

        try:
                c.perform()
        except pycurl.error:
                errno, errstr = pycurl.error
                print ("An error occurred: ", errstr)
                sys.exit(2)
        song = buffer.getvalue()
        if not song:
                print ("No information retrieved from discogs")
                sys.exit(2)
        else:
                #song = song.replace('&', '\&').replace("'", "")
#                print (song)
                print ("hello")

        print('Status: %d' % c.getinfo(c.RESPONSE_CODE))
        print('Status: %f' % c.getinfo(c.TOTAL_TIME))
        if c.getinfo(c.RESPONSE_CODE) == 200:
            buffer.close()
            c.close()
            return (song)
        else:
            response_list = []
            response_str = ""
            print ("error with spotify")
            for char in buffer.getvalue().decode("utf-8"):
                response_list.append(char)
            print (''.join(response_list))
            response_list = list(map(lambda x: x.replace("\n",""), response_list))
            response_str = (''.join(response_list))
            print (response_str)
            if (response_str.find("The access token expired") != -1):
                print ("Getting new access token")
                spotify_token = get_token_from_spotify()
                get_album_from_spotify(song_title, spotify_token)
            buffer.close()
            c.close()
            sys.exit(1)

        # Using readlines()
file1 = open('music.pls', 'r')
Lines = file1.readlines()

count = 0
# Strips the newline character
#for line in Lines:
#    count += 1
#    print("Line{}: {}".format(count, line.strip()))

spotify_token = ""
#for path,dirs,files in os.walk('/opt/shoutcast/mp3/Bhangra'):
for line in Lines:
#    for filename in files:
    pipe = "|"
    bool = False
    list_menu_choices = []
    menu_choices = []
    x = []
    choices_idx = 0
    #print (os.path.join(path,filename))
    filename_orig = line.strip()
    filename = os.path.basename(line.strip())
    song_title = filename.replace(".mp3", "")
    song_title = song_title.replace(" 1", "")
    song_title = song_title.replace(" ", "+")
    song_title = song_title.replace("-", "")
    song_title = song_title.replace("Ft.", "")
    song_title = song_title.replace("Ft", "")
    song_title = song_title.replace("Feat.", "")
    song_title = song_title.replace("Feat", "")
    song_title = song_title.replace("%", "%26")
    song_title = song_title.replace("&", "%20")
    song_title = song_title.replace(".", "%2E")
    song_title = song_title.replace("#", "%23")
    song_title = re.sub("[\(\[].*?[\)\]]", "", song_title)
    print (song_title)

    album = get_album_from_discogs(song_title)
    data = json.loads(album)
    results = (data['results'])
    print (results)

    print ("-------- DISCOGS RESULTS-----")
    for entry in results:
        menu_choices = []
        bool = False
        x = ""
        y = ""
        print (entry['title'])
        id = str(entry['id'])
        uri = (entry['uri'])
        try:
            year = (entry['year'])
        except:
            year = ""
        #print (year)
        choices_idx += 1
        choices_idx_str = str(choices_idx)
        x = entry['title'].split("-")
        if (len(x)) == 2:
            x = (x[1:])
            x = (x[0])
        else:
            x = entry['title']
        #x = entry['title'][-1]
        #x = (x[0])
        x = re.sub("[\(\[].*?[\)\]]", "", x)
        x = (x.replace('*', ''))
        x = (x.replace('  ', ' '))
        x = (x.strip())
        x = x + pipe
        x = x + id
        x = x + pipe
        x = x + uri
        x = x + pipe
        x = x + year
        menu_choices.append(x)
        menu_choices.append(choices_idx_str)
        menu_choices.append(bool)
        list_menu_choices.append(menu_choices)

    menu_choices = []
    choices_idx += 1
    choices_idx_str = str(choices_idx)
    menu_choices.append("---")
    menu_choices.append(choices_idx_str)
    menu_choices.append(bool)
    list_menu_choices.append(menu_choices)

    print ("-------- SPOTIFY RESULTS-----")
    if spotify_token == "":
        spotify_token = get_token_from_spotify()
        print (spotify_token)
    album = get_album_from_spotify(song_title, spotify_token)
    try:
        (artist, title) = filename.split("-", 1)
        artist = artist.strip()
        artist = artist.replace(' 1', '')
        title = title.strip()
        title = title.replace(' 1', '')
        print ("%s - %s" % (artist, title))
    except:
        title = song_title
        print ("%s" % (title))
    #artist_pattern = re.compile(artist)
    #title_pattern = re.compile(title)
    #print (album)
    data = json.loads(album)
    tracks = (data['tracks'])
    #print (tracks)
    print ("---------------------")
    if (tracks['total']) == 0 :
        print ("no data from spotify")
        #sys.exit(0)
    #a1 = (tracks['items'][0])
    a1 = (tracks['items'])
    #print (tracks['items'])
    print ("*********************")
#    for entry, value in a1.items():
#        print (entry)
#        print (value)
    for value in a1:
        talb = ""
        id = ""
        openspot = ""
        choices_idx_str = ""
        bool = False
        print ("\n===============================")
        print (value)
        print ("===============================")
        #if title == value['name']:
        #print (title_pattern)
        #print ("value from spotify")
        print (value['name'])
        #print ("value from file")
        #print (title)
        #if title_pattern.search(value['name']):
        if ((value['name'].find(title) != -1) or (title.find(value['name']) != -1)):
            menu_choices = []
            print ("||||||||||||||||||||||||||")
            choices_idx += 1
            choices_idx_str = str(choices_idx)
            print (value['name'])
            #print (value['external_urls'])
            openspot = (value['external_urls'])
            print (openspot.get('spotify'))
            openspot = openspot.get('spotify')
            id = (value['id'])
            print (value['id'])
            #for album_key, details in range(len(value.items())):
            for album_key, details in value.items():
                if album_key == 'album':
                    #print (album_key)
                    #print (details)
                    for key, value in details.items():
                        if key == 'artists':
                            #print (key)
                        #print (details.values())
                            #print (value)
                            art = value[0]
                            #print (art)
                            print (art.get('name'))
                    #print (list(details.values()))
                    talb = (details.get('name'))
                    print (details.get('name'))
                    print (details.get('release_date'))
                    year = details.get('release_date')
            x = talb
            x = x + pipe
            x = x + id
            x = x + pipe
            x = x + openspot
            x = x + pipe
            x = x + year
            menu_choices.append(x)
            menu_choices.append(choices_idx_str)
            menu_choices.append(bool)
            list_menu_choices.append(menu_choices)
            #sys.exit(0)

    print ("-------- MP3 RESULTS (DEFAULT) -----")

    menu_choices = []
    choices_idx += 1
    choices_idx_str = str(choices_idx)
    menu_choices.append("---")
    menu_choices.append(choices_idx_str)
    menu_choices.append(bool)
    list_menu_choices.append(menu_choices)
    audio = ID3(os.path.join(filename_orig)) #path: path to file

    try:
        print(audio['TPE1'].text[0]) #Artist
    except:
        pass
    try:
        print(audio["TIT2"].text[0]) #Track
    except:
        pass
    try:
        menu_choices = []
        print(" - Album\n%s" % audio["TALB"].text[0]) #Album
        choices_idx += 1
        choices_idx_str = str(choices_idx)
        y = audio["TALB"].text[0]
        y = re.sub("[\(\[].*?[\)\]]", "", y)
        y = (y.replace('*', ''))
        y = (y.replace('  ', ' '))
        y = (y.strip())
        menu_choices.append(y)
        menu_choices.append(choices_idx_str)
        menu_choices.append(bool)
        list_menu_choices.append(menu_choices)
    except:
        print("MP3 Album information not found")

    print ("-------- BLANK RESULTS-----")
    menu_choices = []
    choices_idx += 1
    choices_idx_str = str(choices_idx)
    menu_choices.append("")
    menu_choices.append(choices_idx_str)
    menu_choices.append(bool)
    list_menu_choices.append(menu_choices)

    print (list_menu_choices)
    #tuple_menu_choices = tuple(list_menu_choices)
    #print (tuple_menu_choices)
    list = []
    #list.append(tuple_menu_choices)
    #list.append(list_menu_choices)
    list = list_menu_choices
    print (list)

    txxx = ""
    talb = ""
    tyer = ""
    discogs = ""
    spotify = ""
    song_info1 = ""
    song_info2 = ""
    album = ""
    id = ""
    url = ""
    year = ""

#    list = [['TUTI 21st Chapter (Nachna Aaj Nachna)|22b27xYllfnVRqUXqflNop|https://open.spotify.com/track/22b27xYllfnVRqUXqflNop', '1', False], ['21st Chapter|3
xAFsTxC4BDeFDbei14J9L|https://open.spotify.com/track/3xAFsTxC4BDeFDbei14J9L', '2', False], ['21st Chapter Nachna|4JDmBlrkc3c747u7Etpjdp|https://open.spotify.com/
track/4JDmBlrkc3c747u7Etpjdp', '3', False], ['---', '4', False], ['21st Chapter - Nachna Aaj Nach', '5', False], ['', '6', False]]
#    print (list)
#    list = tuple(list)
#    print (list)

#    sys.exit(0)
    d = Dialog(dialog="dialog")
    d.add_persistent_args(["--no-nl-expand"])
    d.set_background_title("MP3 Album Tagger")


    # We could put non-empty items here (not only the tag for each entry)
#    code, tags = d.checklist("What sandwich toppings do you like?", height=0, width=0,
#                             choices=[("Catsup", "",             False),
#                                      ("Mustard", "",            False),
#                                      ("Pesto", "",              False),
#                                      ("Mayonnaise", "",         True),
#                                      ("Horse radish","",        True),
#                                      ("Sun-dried tomatoes", "", True)],
#                             )

                              #choices = [('21st Chapter (Nachna ajja nachna)|22b27xYllfnVRqUXqflNop|https://open.spotify.com/track/22b27xYllfnVRqUXqflNop', '1',
 False), ('21st Chapter|3xAFsTxC4BDeFDbei14J9L|https://open.spotify.com/track/3xAFsTxC4BDeFDbei14J9L', '2', False), ('21st Chapter Nachna|4JDmBlrkc3c747u7Etpjdp|
https://open.spotify.com/track/4JDmBlrkc3c747u7Etpjdp', '3', False), ('---', '4', False), ('21st Chapter - Nachna Aaj Nach', '5', False), ('', '6', False)]
#                            )


#    code, tag = d.menu(filename, height=0, width=0,
#              choices=list)
#    list = [('Bud 21st Chapter (Nachna Aaj Nachna)|22b27xYllfnVRqUXqflNop|https://open.spotify.com/track/22b27xYllfnVRqUXqflNop', '1', False), ('21st Chapter|3x
AFsTxC4BDeFDbei14J9L|https://open.spotify.com/track/3xAFsTxC4BDeFDbei14J9L', '2', False), ('21st Chapter Nachna|4JDmBlrkc3c747u7Etpjdp|https://open.spotify.com/t
rack/4JDmBlrkc3c747u7Etpjdp', '3', False), ('---', '4', False), ('21st Chapter - Nachna Aaj Nach', '5', False), ('', '6', False)]

    code, tag = d.checklist(filename, height=0, width=0, choices=list)
    if code == d.OK:
        print (tag)
        #t = tag.split("|")
        #album_info = (t[0])
        #custom_info = ("Discogs|%s|%s" % ((t[1]), (t[2])))
        #print ("Tagging file %s with:" % filename_orig)
        #print ("- TALB: %s" % album_info)
        #print ("- TXXX: %s" % custom_info)

        print (len(tag))

        if (len(tag)) > 2:
            print ("Expecting 1 or 2 details to be processed")
            d.msgbox("Expecting 1 or 2 details to be processed")
            #sys.exit(0)

        if (len(tag)) <= 2:
            print (tag)
            # Check to see if not formatted
            try:
                song_info1 = ((tag)[0])
                (album, id, url, year) = song_info1.split("|")
            except:
                print (("\n%s - Not formatted, so its just an album name") % song_info1)
                talb = song_info1
            try:
                song_info1 = ((tag)[0])
                print ((tag)[0])
                song_info1 = song_info1.split("|")
            except:
                print ("Could not find a 1st list entry")

            # Check to see if not formatted
            try:
                song_info2 = ((tag)[1])
                (album, id, url, year) = song_info2.split("|")
            except:
                print (("\n%s - Not formatted, so its just an album name or no second info obtained") % song_info2)
                talb = song_info1
            try:
                song_info2 = ((tag)[1])
                print ((tag)[1])
                song_info2 = song_info2.split("|")
            except:
                print ("Could not find a 2nd list entry")

            # Determine which info is discogs or spotify
            #print ((song_info1)[1])
            #print ((song_info2)[1])

            if (song_info1) != "":
                try:
                    if ((song_info1)[1]).isdigit():
                        print ("Digits for ID found, must be discogs")
                        song_info1[2] = "https://discogs.com" + song_info1[2]
                        discogs = song_info1
                        talb = song_info1[0]
                        tyer = song_info1[3]
                    else:
                        spotify = song_info1
                        talb = song_info1[0]
                        tyer = song_info1[3]
                except:
                    print ("")

            if (song_info2) != "":
                try:
                    if ((song_info2)[1]).isdigit():
                        print ("Digits for ID found, must be discogs")
                        song_info2[2] = "https://discogs.com" + song_info2[2]
                        discogs = song_info2
                        talb = song_info2[0]
                        tyer = song_info2[3]
                    else:
                        spotify = song_info2
                        talb = song_info2[0]
                        tyer = song_info2[3]
                except:
                    print ("")


        print (("Discogs => %s") % discogs)
        print (("Spotify => %s") % spotify)

        print ("")
        print ("")
        print ("Compile the TXXX string tag")

        #discogs = '|'.join(discogs)
        #discogs = 'Discogs|' + discogs
        #print (("Discogs => %s") % discogs)
        #spotify = '|'.join(spotify)
        #spotify = 'Spotify|' + spotify
        #print (("Spotify => %s") % spotify)

        if discogs != "":
            del discogs[3:]
            discogs = '|'.join(discogs)
            discogs = 'Discogs|' + discogs
            txxx = discogs
        if spotify != "":
            del spotify[3:]
            spotify = '|'.join(spotify)
            spotify = 'Spotify|' + spotify
            txxx = spotify
        if discogs != "" and spotify != "":
            txxx = discogs + "*" + spotify

        if len(tag) == 0:
            print ("Tagging nothing")

        try:
            (year, month, day) = tyer.split("-")
            tyer = year
        except:
            print ("Cannot split the year format or no year given")

        print (("TXXX - %s") % txxx)
        #talb = ''.join(talb)
        print (("TALB - %s") % talb)
        print (("TYER - %s") % tyer)

        """
        # If album information only, TXXX = blank, TALB = album info, TYER = no_change
        # If discogs information only, TXXX = discogs url, TALB = discogs album info, TYER = discogs year
        # If spotify information only, TXXX = spotify url, TALB = spotify album info, TYER = spotify year
        # If blank information only, TXXX = blank, TALB = blank, TYER = leave
        """
        if talb != "" and tyer == "" and txxx == "":
            print ("Tagging Album information only!")
            add_id3_info(filename_orig, talb, True, txxx, False, tyer, False)
        elif talb != "" and tyer != "" and txxx != "":
            print ("Tagging all TALB, TYER and TXXX!")
            add_id3_info(filename_orig, talb, True, txxx, True, tyer, True)
        elif talb == "" and tyer == "" and txxx == "":
            print ("Tagging TALB, TYER and TXXX with blanks")
            add_id3_info(filename_orig, talb, True, txxx, True, tyer, True)
        elif talb != "" and tyer == "" and txxx != "":
            print ("Tagging TALB, TXXX only")
            add_id3_info(filename_orig, talb, True, txxx, True, tyer, False)

#        add_id3_info(filename_orig, album_info, custom_info )
        pass



    album = input("\n-------------\nOK...")
    #print (album)

    print ("\n-------------\n\n")

sys.exit(0)
#album = get_album_from_discogs("Balwinder Safri - Putt Sardaran De")
#album = get_album_from_discogs("Aman Hayer - Dil Nai Lagda")
#album = get_album_from_discogs("Dr Zeus - Ah Ni Kuria")
#album = get_album_from_discogs("Nav Sarao - Hasdi Hasdi")
#album = get_album_from_discogs("KS Bhamrah - Giddha Sare")
#print (album)

data = json.loads(album)
#print (data)

#print(json.dumps(data, indent = 4, sort_keys=True))

results = (data['results'])

print ("-------- DISCOGS RESULTS-----")
for entry in results:
    #print (entry)
    print (entry['title'])

print ("-------- MP3 RESULTS (DEFAULT) -----")
from mutagen.id3 import ID3

audio = ID3("/opt/shoutcast/mp3/Bhangra/Nav Sarao - Hasdi Hasdi.mp3") #path: path to file

print(audio['TPE1'].text[0]) #Artist
print(audio["TIT2"].text[0]) #Track
print(" - Album\n%s" % audio["TALB"].text[0]) #Album

print ("-------- ARCLOUD RESULTS-----")

album = input("\n-------------\nEnter your choice for album or press Enter to accept default...")

print (album)
