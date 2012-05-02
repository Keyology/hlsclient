from collections import namedtuple
import m3u8
import hlsclient.consumer

Key = namedtuple('Key', 'uri')

class BaseFakeM3U8(object):
    def load(self, uri):
        pass

    @property
    def key(self):
        return Key(uri=None)

def test_if_consume_loads_path(monkeypatch):
    called_args = []
    class FakeM3U8(BaseFakeM3U8):
        def load(self, url):
            called_args.append(url)

    monkeypatch.setattr(m3u8.model, 'M3U8', FakeM3U8)
    hlsclient.consumer.consume('uri', '/path')
    assert ['uri'] == called_args

def test_if_consume_downloads_key_file(monkeypatch):
    class FakeM3U8(BaseFakeM3U8):
        @property
        def key(self):
            return Key('/key')
    monkeypatch.setattr(m3u8.model, 'M3U8', FakeM3U8)

    called_args = []
    def fake_download_to_file(uri, local_path):
        assert '/key' == uri
        assert local_path
        called_args.append(uri)
    monkeypatch.setattr(hlsclient.consumer, 'download_to_file',
        fake_download_to_file)
    hlsclient.consumer.consume('uri', '/path')
    assert 1 == len(called_args)