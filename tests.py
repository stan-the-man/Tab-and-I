from helpers import Tab, play_tab, SpotifyAccess, TabAndI
import json

class TestTab(object):
    def __init__(self):
        self.lines = [
             """E|---1---1--3|\n
             B|-0-2---3---|\n
             G|---1---3-5-|\n
             D|---4---3---|\n
             A|---4---1---|\n
             E|---1-------|\n
             THIS IS A LINE\n
             ' ',\n
             E|---1---1--3|\n
             B|-0-2---3---|\n
             G|---1---3-5-|\n
             D|---4---3---|\n
             A|---4---1---|\n
             E|---1-------|\n
             """
        ]
        with open('output.json') as data:
            self.raw_tab_info = json.load(data)
        self.metallica = Tab(self.raw_tab_info[0])
        self.zepplin = Tab(self.raw_tab_info[1])
        fake_tab_info = {
                'tuning': 'Standard',
                'tab': self.lines,
                'tab_author': 'Stan Whitcomb',
                'capo': 'No capo',
                'artist': 'Band Practice',
                'song': 'Helicopter Mom',
        }
        self.fake_tab = Tab(fake_tab_info)


    def test_import(self):
        assert self.metallica.tab == self.raw_tab_info[0]['tab']
        assert self.zepplin.tab == self.raw_tab_info[1]['tab']

    def test_separate_lines(self):
        strings = self.fake_tab.separate_into_strings(self.lines[0].split('\n'))
        assert sorted(strings.keys()) == sorted(['Eh','A','D','G','B','El'])
        assert strings['Eh'] == '|---1---1--3|---1---1--3|'
        assert strings['El'] == '|---1-------|---1-------|'

    def test_strings(self):
        assert sorted(self.zepplin.strings.keys()) == sorted(['Eh','A','D','G','B','El'])
        assert self.zepplin.strings['Eh'][:19] == '|-------5-7-----7-|'

    def test_slice(self):
        strings_slice = self.fake_tab.slice_tab(0,11)
        assert strings_slice['Eh'] == '|---1---1--'
        assert strings_slice['B'] == '|-0-2---3--'
        assert strings_slice['G'] == '|---1---3-5'
        assert self.fake_tab.slice_tab(5,16)['D'] == '---3---|---'
        assert strings_slice['A'] == '|---4---1--'
        assert strings_slice['El'] == '|---1------'

    def test_printing(self):
        play_tab(self.zepplin, .2, 30)

    def test_order_strings(self):
        assert self.fake_tab.order_strings() == ['Eh','B','G','D','A','El'] 

    def test_length(self):
        assert self.fake_tab.tab_length == 25
        self.fake_tab.strings[self.fake_tab.strings.keys()[0]] += '----'
        assert self.fake_tab.tab_length == 25


class TestSpotifyAccess(object):
    def __init__(self):
        self.spotify = SpotifyAccess('Stan Whitcomb')
        self.test_playlist_id = u'7wXA76L2L3C90Mj3IgAbaS'

    def test_connection_to_spotify(self):
        assert self.spotify.token
        assert self.spotify.connection

    def test_information(self):
        assert self.spotify.connection.me()['display_name'] == 'Stan Whitcomb'

    def test_get_playlist(self):
        assert len(self.spotify.get_playlist(self.test_playlist_id)) == 2

    def test_get_artist_and_song_from_playlist(self):
        test_artist_song_dict = [
                ('Led Zeppelin', 'Stairway To Heaven'),
                ('Metallica', 'Nothing Else Matters')
                ]
        assert self.spotify.get_artist_and_song_from_playlist(self.test_playlist_id) == test_artist_song_dict

    def test_urls_to_scrape(self):
        artist_song_list = self.spotify.get_artist_and_song_from_playlist(self.test_playlist_id)
        urls = self.spotify.get_urls_to_scrape_from_spotify(artist_song_list)
        assert urls[0] == 'https://tabs.ultimate-guitar.com/l/led_zeppelin/stairway_to_heaven_tab.htm'

    def test_get_tempo(self):
        self.spotify.get_song_tempo('5CQ30WqJwcep0pYcV4AMNc') == 482


class TestTabAndI(object):
    def __init__(self):
        self.tab = TabAndI()

    def test_mongo_connection(self):
        assert self.tab.mongo.myCollection.find_one()['x'] == 1

    def test_find_tab(self):
        song = 'STAIRWAY TO HEAVEN'
        artist = 'Led Zeppelin'
        # should print the tab
        assert self.tab.get_tab_from_mongo(song=song, artist=artist)['artist'] == artist
        assert self.tab.get_tab_from_mongo(song=song)['artist'] == artist
        assert self.tab.get_tab_from_mongo() == None

    def test_play_tab_from_mongo(self):
        song = 'STAIRWAY TO HEAVEN'
        artist = 'Led Zeppelin'
        raw_tab_info = self.tab.get_tab_from_mongo(song=song, artist=artist)

        tab = Tab(raw_tab_info)
        play_tab(tab, .02, 30)

test_tab = TestTab()
test_spotify = TestSpotifyAccess()
test_tab_and_i = TestTabAndI()

test_tab.test_import()
test_tab.test_separate_lines()
test_tab.test_strings()
test_tab.test_slice()
test_tab.test_order_strings()
#test_tab.test_printing()
TestTab().test_length()

test_spotify.test_connection_to_spotify()
test_spotify.test_information()
test_spotify.test_get_playlist()
test_spotify.test_urls_to_scrape()
test_spotify.test_get_tempo()

test_tab_and_i.test_mongo_connection()
test_tab_and_i.test_find_tab()
#test_tab_and_i.test_play_tab_from_mongo()
