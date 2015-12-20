import itertools
import os
import random
import sys
import time

try:
    from http.client import HTTPException
except ImportError:
    from httplib import HTTPException
try:
    from xmlrpc.client import ProtocolError
except ImportError:
    from xmlrpclib import ProtocolError

import gzip
try:
    from StringIO import StringIO
except ImportError:
    pass

import requests
from pythonopensubtitles.opensubtitles import OpenSubtitles

from tv_series import common


DEFAULT_TIMEOUT = 15
FILE_NAME_DOWNLOADED = 'episode_ids_downloaded.txt'
FILE_NAME_ERROR = 'episode_ids_failed.txt'


def _gzip_decompress(s):
    """Decompress a gzip compressed string.
    Compatible with both Python 2 and 3."""
    try:
        return gzip.decompress(s)
    except AttributeError:
        with gzip.GzipFile(fileobj=StringIO(s)) as f:
            return f.read()


def download_subs(ids, excl, dir_path, opensub, timeout=0):
    for id in ids:
        if id in excl:
            print('IMDB ID SKIPPED {}'.format(id))
            continue
        print('IMDB ID {}'.format(id))
        try:
            if timeout:
                time.sleep(timeout)
            subs = opensub.search_subtitles([{
                'imdbid': id,
                'sublanguageid': 'eng'
            }])
        except HTTPException as e:
            print('  ERROR HTTP exception {}'.format(e))
            continue
        except ProtocolError as e:
            print('  ERROR XML-RPC exception {}'.format(e))
            continue
        if not subs:
            print('  ERROR Subtitles not found')
            continue
        sub = subs[0]
        file_path = os.path.join(dir_path, sub['SubFileName'])
        if os.path.isfile(file_path):
            print(u'  ALREADY DOWNLOADED {} {}'
                  .format(sub['SubFileName'], sub['SubDownloadLink']))
            continue
        print(u'  DOWNLOADING {} {}'
              .format(sub['SubFileName'], sub['SubDownloadLink']))
        r = requests.get(sub['SubDownloadLink'])
        if r.status_code != 200 or not r.content:
            print(u'  ERROR HTTP request failed, status_code={}, text={}'
                  .format(r.status_code, r.text))
            continue
        with open(file_path, 'wb') as f:
            print(u'  WRITING {}'.format(file_path))
            f.write(_gzip_decompress(r.content))
            yield (id, sub['SubFileName'])


def download_subs_and_cache_results():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Download subtitles for movies specified'
        ' by passed IMDB IDs'
    )
    parser.add_argument('--input', '-i', dest='inputfile', required=True,
                        help='IMDB IDs list file -- one IMDB ID per line')
    parser.add_argument('--output', '-o', dest='outputdir', required=True,
                        help='path to a directory in which the subtitle SRT'
                        ' files will be downloaded')
    parser.add_argument('--cache', '-c', dest='cachedir', required=True,
                        help='cache location')
    parser.add_argument('--shuffle', '-s', dest='shuffle', action='store_true',
                        help='shuffle the list of IMDB IDs')
    parser.add_argument('--timeout', '-t', dest='timeout', type=int,
                        default=DEFAULT_TIMEOUT,
                        help='time in seconds between OpenSubtitles\'s API'
                        ' calls, if not set {} is used'
                        .format(DEFAULT_TIMEOUT))
    args = parser.parse_args()

    opensub = OpenSubtitles()
    opensub.login(os.environ['OPENSUB_USER'], os.environ['OPENSUB_PASSWD'])

    ids = common.read_list_from_file(args.inputfile)
    if args.shuffle:
        random.shuffle(ids)

    # Need to call list to make the list concatenation work in Python 2.
    excl = list(itertools.chain.from_iterable(
        [common.read_list_from_file(os.path.join(args.cachedir, f))
         for f in (FILE_NAME_DOWNLOADED, FILE_NAME_ERROR)]
    ))

    common.write_list_to_file(
        os.path.join(args.cachedir, FILE_NAME_DOWNLOADED),
        download_subs(
            ids,
            excl,
            args.outputdir,
            opensub,
            timeout=args.timeout
        )
    )

    sys.exit()


if __name__ == '__main__':
    download_subs_and_cache_results()
