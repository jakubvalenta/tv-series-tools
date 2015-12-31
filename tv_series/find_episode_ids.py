import sys

import listio
from imdb import IMDb
from imdb import IMDbDataAccessError


def find_episode_ids(series_titles, ia):
    for series_title in series_titles:
        print('FIND ' + series_title)
        ids = []
        ia_result = ia.search_movie(series_title)
        if not ia_result:
            print(ia_result)
            print('  ERROR Movie not found')
            continue
        ia_movie = [0]
        for ia_movie in ia_result:
            print(u'MOVIE {0}'.format(ia_movie['long imdb canonical title']))
            ia.update(ia_movie)
            if ia_movie['kind'] != 'tv series':
                print('  ERROR Not a TV series')
                continue
            try:
                ia.update(ia_movie, 'episodes')
                try:
                    if not ia_movie['episodes']:
                        continue
                except KeyError as e:
                    print(e)
                    continue
                for season_no, episodes in ia_movie['episodes'].items():
                    for episode_no, episode in episodes.items():
                        print(u'  EPISODE S{0:02d}E{1:02d} [{2}] {3}'.format(
                            int(season_no),
                            int(episode_no),
                            episode.movieID,
                            episode['title']
                        ))
                        yield (
                            episode.movieID,
                            episode['long imdb episode title']
                        )
            except IMDbDataAccessError as e:
                print(e)
            break


def find_and_write_episode_ids():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Find IMDB IDs for all episodes of ' +
        'passed TV series'
    )
    parser.add_argument('--input', '-i', dest='inputfile', required=True,
                        help='TV series list file -- one series title per'
                        ' line, empty lines and lines starting with the hash'
                        ' sign are ignored')
    parser.add_argument('--output', '-o', dest='outputfile', required=True,
                        help='output file -- episode IMDB IDs will be written'
                        ' one ID per line, if the file exists it will not be'
                        ' overwritte, but IMDB IDs not already included in the'
                        ' file will be added')
    args = parser.parse_args()

    listio.write_map(
        args.outputfile,
        find_episode_ids(
            listio.read_list(args.inputfile),
            IMDb()
        )
    )

    sys.exit()


if __name__ == '__main__':
    find_and_write_episode_ids()
