from bottle import route, run, response
import bottle


M3U8_SERVER = 'http://localhost:8845'

VARIANT_PLAYLIST = '''\
#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2560000
/high.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1280000
/low.m3u8
'''.format(server=M3U8_SERVER)


@route('/variant.json')
def variant_json():
    return '''\
{
    "actives": [{
        "m3u8": "/hls-with-mbr.m3u8",
        "servers": [],
        "bitrates": [
            {"m3u8": "/low.m3u8", "servers": ["http://serv1.com:80", "http://serv2.com:1234"], "bandwidth": 1280000},
            {"m3u8": "/high.m3u8", "servers": ["http://serv1.com:81", "http://serv2.com:2345"], "bandwidth": 2560000}
        ],
        "needs_index": true
    }]
}
'''


@route('/variant-playlist.m3u8')
def variant_playlist():
    response.set_header('Content-Type', 'application/vnd.apple.mpegurl')
    return VARIANT_PLAYLIST


@route('/low.m3u8')
@route('/live/low.m3u8')
def low_playlist():
    response.set_header('Content-Type', 'application/vnd.apple.mpegurl')
    return '''\
#EXTM3U
#EXT-X-TARGETDURATION:200
#EXTINF:100,
{server}/low1.ts
#EXTINF:100,
{server}/low2.ts
#EXT-X-ENDLIST
'''.format(server=M3U8_SERVER)


@route('/high.m3u8')
def high_playlist():
    response.set_header('Content-Type', 'application/vnd.apple.mpegurl')
    return '''\
#EXTM3U
#EXT-X-TARGETDURATION:200
#EXTINF:100,
{server}/high1.ts
#EXTINF:100,
{server}/high2.ts
#EXT-X-ENDLIST
'''.format(server=M3U8_SERVER)

@route('/crypto.m3u8')
def crypto_playlist():
    response.set_header('Content-Type', 'application/vnd.apple.mpegurl')
    return '''\
#EXTM3U
#EXT-X-MEDIA-SEQUENCE:82400
#EXT-X-ALLOW-CACHE:NO
#EXT-X-VERSION:2
#EXT-X-KEY:METHOD=AES-128,URI="/key.bin", IV=0X10ef8f758ca555115584bb5b3c687f52
#EXT-X-TARGETDURATION:200
#EXTINF:100,
{server}/high1.ts
#EXTINF:100,
{server}/high2.ts
#EXT-X-ENDLIST
'''.format(server=M3U8_SERVER)

@route('/missing_chunks.m3u8')
def missing_chunks_playlist():
    response.set_header('Content-Type', 'application/vnd.apple.mpegurl')
    return '''\
#EXTM3U
#EXT-X-TARGETDURATION:200
#EXTINF:100,
{server}/missing1.ts
#EXTINF:100,
{server}/missing2.ts
#EXT-X-ENDLIST
'''.format(server=M3U8_SERVER)


@route('/key.bin')
def key():
    return 'FAKE KEY\n'

@route('/<:re:(high|low)(1|2)>.ts')
def chunk():
    return 'FAKE TS\n'

if __name__ == '__main__':
    bottle.debug = True
    run(host='localhost', port=8845)
