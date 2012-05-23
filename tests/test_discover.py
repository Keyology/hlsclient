import ConfigParser
import io
import os

import hlsclient.discover
from hlsclient.discover import Server, PlaylistDiscover

from tests.fake_m3u8_server import VARIANT_PLAYLIST, M3U8_SERVER

def test_discovers_simple_m3u8_from_api_url_in_config(monkeypatch):
    sample_config = """[discover]
api_url = http://localhost:4422/tests.m3u8
"""
    config = ConfigParser.RawConfigParser()
    config.readfp(io.BytesIO(sample_config))

    def fake_get_info_from_url(url):
        # m3u8 sample got from http://webme.ws/live-docs/thorp.html
        return [{
            'm3u8': '/hls-without-mbr.m3u8',
            'servers': ['http://serv1.com', 'http://serv2.com'],
            'bitrates': [],
            'needs_index': False,
        }]

    monkeypatch.setattr(hlsclient.discover, 'get_info_from_url', fake_get_info_from_url)
    discover = PlaylistDiscover(config)

    playlist = '/hls-without-mbr.m3u8'
    servers = [Server(server='http://serv1.com', port=80), Server(server='http://serv2.com', port=80)]
    assert {playlist: servers} == discover.playlist_paths


def test_discovers_simple_m3u8_from_api_url_in_config(monkeypatch):
    sample_config = """[discover]
api_url = http://localhost:4422/mbr-tests.m3u8
"""
    config = ConfigParser.RawConfigParser()
    config.readfp(io.BytesIO(sample_config))

    def fake_get_info_from_url(url):
        # m3u8 sample got from http://webme.ws/live-docs/thorp.html
        return [{
            'm3u8': '/hls-with-mbr.m3u8',
            'servers': [],
            'bitrates': [
                {'m3u8': '/hls100.m3u8', 'servers': ['http://serv1.com:80', 'http://serv2.com:1234'], 'bandwidth': 100},
                {'m3u8': '/hls200.m3u8', 'servers': ['http://serv1.com:81', 'http://serv2.com:2345'], 'bandwidth': 200},
                {'m3u8': '/hls300.m3u8', 'servers': ['http://serv1.com:82', 'http://serv2.com:3456'], 'bandwidth': 300}
            ],
            'needs_index': True,
        }]

    monkeypatch.setattr(hlsclient.discover, 'get_info_from_url', fake_get_info_from_url)

    discover = PlaylistDiscover(config)

    low_playlist = '/hls100.m3u8'
    mid_playlist = '/hls200.m3u8'
    high_playlist = '/hls300.m3u8'
    expected_result = {
        low_playlist: [Server('http://serv1.com', port=80), Server('http://serv2.com', 1234)],
        mid_playlist: [Server('http://serv1.com', port=81), Server('http://serv2.com', 2345)],
        high_playlist: [Server('http://serv1.com', port=82), Server('http://serv2.com', 3456)],
    }

    assert expected_result == discover.playlist_paths

def test_PlaylistDiscover_should_create_m3u8_for_variant_playlists(tmpdir):
    variant_config = """[discover]
api_url = {host}/variant.json
""".format(host=M3U8_SERVER)
    config = ConfigParser.RawConfigParser()
    config.readfp(io.BytesIO(variant_config))

    discover = PlaylistDiscover(config)
    discover.create_index_for_variant_playlists(str(tmpdir))

    filepath = str(tmpdir.join('hls-with-mbr.m3u8'))

    assert os.path.exists(filepath)
    assert VARIANT_PLAYLIST == open(filepath).read()
