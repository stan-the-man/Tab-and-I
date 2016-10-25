import time
import os
import re
import spotipy
import spotipy.util
from tutorial.settings import MONGO_DATABASE
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from pymongo import MongoClient

# Things to do:

# Shit I have accomplished:

# [x] move output.json into this repo
# [x] find a way to deal with the line separations for each key.
# [x] make sure that line separations are done by the keys found... 
# [x] consider making strings its own class instead of a dictionary
        # for now will not use a class. No need at the moment.
        # not gaining anything with a class implementation.
# [x] should I be storing all these in dictionaries or in list?
        # storing in a dictionary because it facilitates
        # entry as well as allowing me to know specific strings
        # and access them.
        # list wouild give better ordering for printing, but I can
        # just convert on the fly.
# [x] print slices of each string
# [x] find a way to advance the slices cleanly
# [x] successfully access spotify through spotipy
# [x] access the correct playlist to get the songs for scrapping
# [x] get the song information (in this case I need tempo)
# [x] create a DB that holds all the songs I have already scraped
# [x] store all info in a mongoDB to make this robust and scalable.
# [x] connect to the mongo DB to get the new songs.
# [x] play a tab from the mongo DB instead of the output.json
# [x] scrape for new songs from spotify and add them to mongo tests

# Things to do generally

# [] handle case where cant find a tab
        # currently I error out on the conversion to a Tab feature
        # I may want to return a Tab construct from that search
        # instead of a DB file.

# Things to do with Mongo DB

# [] explore a cache system to see if anything has changed for scraping
# [] make sure that all information that goes in to the DB is uniform
        # for this I will have to delete the Nothing Else Matters and
        # Stairway to Heaven entries and re-scrape

# Things to do with the Interface

# [] build an interface to select the song I want
# [] explore ways to link this information to a frontend application

# Things to do with Spotify

# [] clean up the way SpotifyAccess handles the info
# [] edit the spotipy source code so that I can get the other info available from echonest
# [] figure out a way to link the tempo to the timing of how the tab is presented

# main url for tabs website that I scrape
MAIN_URL = 'https://tabs.ultimate-guitar.com/'
# this is the ID for the "Songs I Want to Learn" playlist
# from spotify
PLAYLIST_ID = u'63Df73bh2ySz0rR88znk26'

# musical notes dictionary to correspond them with a number
notes = {
    'C': 0,
    'C#': 1,
    'D': 2,
    'D#': 3,
    'E': 4,
    'F': 5,
    'F#': 6,
    'G': 7,
    'G#': 8,
    'A': 9,
    'A#': 10,
    'B': 11,
}


class SpotifyAccess(object):
    def __init__(self, username, state=None):
        self.username = username
        self.state = state or 'user-library-read'

    # returns an access token to use the spotify API
    @property
    def token(self):
        return spotipy.util.prompt_for_user_token(self.username, self.state)

    # returns the connection object to use with spotipy
    @property
    def connection(self):
        return spotipy.Spotify(auth=self.token)

    # returns my userID for spotipy useage
    @property
    def id(self):
        return self.connection.me()['id']

    # gets the song information from a playlist ID
    def get_playlist(self, playlist_id):
        return self.connection.user_playlist(
                    self.id, playlist_id=playlist_id)['tracks']['items']

    # returns a list of tuples of the artist and song of a playlist
    # playlist must come in the form of a playlist ID
    # for now this playlist ID will be preset in the code.
    def get_artist_and_song_from_playlist(self, playlist_id):
        return [(song['track']['artists'][0]['name'],
                song['track']['name']) for song in self.get_playlist(playlist_id)]

    def get_urls_to_scrape_from_spotify(self, artist_song_list):
        return [construct_url(artist, song)
                for artist, song in artist_song_list]

    # returns the duration of the song in seconds.
    def get_song_tempo(self, song_id):
        return self.connection.track(song_id)['duration_ms'] / 1000


def construct_url(artist, song):
    artist = re.sub(' ', '_', artist).lower()
    song = re.sub(' ', '_', song).lower()
    return MAIN_URL + artist[0] + '/' + artist + '/' + song + '_tab.htm'


def get_artist_and_song_from_input():
    print "type: artist-song"
    return tuple(re.sub(' ', '_', raw_input().lower()).split('-'))


class TabAndI(object):
    username = 'Stan Whitcomb'
    tabs_db_name = 'Tab_Store'
    tabs_collection_name = 'tabs'
    songs_collection_name = 'songs'

    def __init__(self):
        self.spotify = SpotifyAccess(self.username)
        self.mongo_uri = None
        self.mongo_db = MONGO_DATABASE

    @property
    def mongo(self):
        client = MongoClient('localhost', 27107)
        return client[self.tabs_db_name]

    # this access spotify to get the current list of songs
    # then scrapes any new songs for tabs and adds them to the DB
    def check_n_scrape(self):
        artist_song_list = self.spotify.get_artist_and_song_from_playlist(PLAYLIST_ID)
        urls = self.spotify.get_urls_to_scrape_from_spotify(artist_song_list)
        self.crawl_url_list(urls)

    # takes a set of new urls and gets the ones that have not been seen before
    # using symetric difference of sets.
    def only_new_urls(self, urls):
        # access DB that holds list of urls
        # retunrn it in the form of a set
        known_songs = set()
        url_set = set(urls)
        return url_set - known_songs

    # creates a spider and sets it start urls as the given urls
    # then crawls with that spider.
    def crawl_url_list(self, urls):

        process = CrawlerProcess(get_project_settings())
        process.crawl('tabs', start_urls=list(self.only_new_urls(urls)))
        process.start()

    # gets a tab given a song name, an artist name, or both.
    # for artist name will return a single song from that artist.
    def get_tab_from_mongo(self, song=None, artist=None):
        query = {}
        if song:
            query['song'] = song
        if artist:
            query['artist'] = artist
        return None if query == {} else self.mongo.tabs.find_one(query)

def play_tab(tab, timing, window):
        start = 0
        end = window
        while end < tab.tab_length:
            os.system('cls' if os.name == 'nt' else 'clear')
            print tab.print_slice(start, end)
            time.sleep(timing)
            start += 1; end += 1


class Tab(object):
    def __init__(self, raw_tab_data):
        self.tuning = raw_tab_data['tuning']
        self.tab = raw_tab_data['tab']
        self.tab_author = raw_tab_data['tab_author']
        self.capo = raw_tab_data['capo']
        self.artist = raw_tab_data['artist']
        self.song = raw_tab_data['song']

    @property
    def strings(self):
        return self.separate_into_strings(self.tab[0].split('\n'))

    @property
    def tab_length(self):
        return min([len(v) for k, v in self.strings.iteritems()])

    def separate_into_strings(self, lines):
        strings = dict()
        # used for telling which E we are using
        Ehi = True
        for line in lines:
            if '|' in line and line[0] != '|':
                line = re.sub('\s', '', line)
                key, string_tab = line.split('|', 1)
                if key == 'E':
                    key = 'Eh' if Ehi else 'El'
                    Ehi = not Ehi
                if not strings.get(key):
                    strings[key] = '|' + string_tab
                else:
                    strings[key] += string_tab
        return strings

    def slice_tab(self, start, end):
        return {string: tab[start:end] for string,tab in self.strings.iteritems()}

    def order_strings(self):
        # returns a list with the strings in order from high -> low
        # for now only dealing with standard tunings. No drop D
        # means no rage against the machine :P
        # steps go 7,7,8,7,7
        # 0 - 11 (12 notes) starts with lowest (usually going to be E)
        # how many steps separate notes.
        strings = []
        nums_to_notes = {v: k for k,v in notes.iteritems()}
        start_note = [note for note in self.strings.keys() if 'h' in note][0]
        start_num = notes[start_note[:-1]]
        strings.append(start_note)
        strings.append(nums_to_notes[(start_num + 7) % 12])
        strings.append(nums_to_notes[(start_num + 7 + 8) % 12])
        strings.append(nums_to_notes[(start_num + 7 + 8 + 7) % 12])
        strings.append(nums_to_notes[(start_num + 7 + 8 + 7 + 7) % 12])
        strings.append(nums_to_notes[(start_num + 7 + 8 + 7 + 7 + 7) % 12] + 'l')
        return strings

    def print_slice(self, start, end):
        printable = ''
        sliced_tab = self.slice_tab(start, end)
        for string in self.order_strings():
            printable += sliced_tab[string] + '\n'
        return printable
