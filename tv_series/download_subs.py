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

import listio
import requests
from pythonopensubtitles.opensubtitles import OpenSubtitles


DEFAULT_TIMEOUT = 15
FILE_NAME_DOWNLOADED = 'subtitles_downloaded.csv'
FILE_NAME_FAILED = 'subtitles_failed.csv'


def _gzip_decompress(s):
    """Decompress a gzip compressed string.
    Compatible with both Python 2 and 3."""
    try:
        return gzip.decompress(s)
    except AttributeError:
        with gzip.GzipFile(fileobj=StringIO(s)) as f:
            return f.read()


def download_subs(movies, excl_ids, dir_path, opensub, timeout=0):
    for id, title in movies:
        print('MOVIE {} {}'.format(id, title))
        if id in excl_ids:
            print('  SKIPPED')
            continue
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
            yield (id, None, 'ERROR Subtitles not found')
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
            yield (id, sub['SubFileName'], None)


def write_result(file_path_success, file_path_failed, results):
    for id, sub_file_name, error in results:
        if error is None:
            listio.write_map(file_path_success, [(id, sub_file_name)])
        else:
            listio.write_map(file_path_failed, [(id, error)])


def download_subs_and_cache_results():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Download subtitles for movies specified'
        ' by passed IMDB IDs'
    )
    parser.add_argument('--input', '-i', dest='inputfile', required=True,
                        help='movies CSV file: 1st column = IMDB ID, 2nd column = title')
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

    movies = listio.read_map(args.inputfile)
    if args.shuffle:
        movies = list(movies)
        random.shuffle(movies)

    excl_ids = []
    for f in (FILE_NAME_DOWNLOADED, FILE_NAME_FAILED):
        try:
            lines = listio.read_map(os.path.join(args.cachedir, f))
            for line in lines:
                excl_ids.append(line[0])
        except FileNotFoundError:
            pass

    if not os.path.isdir(args.cachedir):
        os.makedirs(args.cachedir)
    if not os.path.isdir(args.outputdir):
        os.makedirs(args.outputdir)

    write_result(
        os.path.join(args.cachedir, FILE_NAME_DOWNLOADED),
        os.path.join(args.cachedir, FILE_NAME_FAILED),
        download_subs(
            movies,
            excl_ids,
            args.outputdir,
            opensub,
            timeout=args.timeout
        )
    )

    sys.exit()


if __name__ == '__main__':
    download_subs_and_cache_results()
