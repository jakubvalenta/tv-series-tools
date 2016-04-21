# TV Series Tools

- Download subtitles for all TV series episodes.
- Search subtitles for specific expressions.

## Installation

This software requires Python 2.7. See [Python's website](https://www.python.org/) for installation instructions.

When you have Python 2.7 installed, install required packages with pip (Python's package management system):

```
pip2 install listio
pip2 install requests
pip2 install imdbpy
pip2 install "git+https://github.com/agonzalezro/python-opensubtitles#egg=python-opensubtitles"
pip2 install pysrt
pip2 install termcolor
pip2 install moviepy
```

Then you can call the executables:

```
./tv-series-download-subs -h
./tv-series-find-episode-ids -h
./tv-series-search-subs -h
./tv-series-matches-approve -h
./tv-series-matches-check-approved -h
./tv-series-matches-print-approved -h
```

Or you can install this software as a Python package, which will also install all the dependencies and make the executables available globally:

```
python2 setup.py install

tv-series-download-subs -h
tv-series-find-episode-ids -h
tv-series-search-subs -h
tv-series-matches-approve -h
tv-series-matches-check-approved -h
tv-series-matches-print-approved -h
```

## Usage

This software works in several phases:

### 1. Find IMDB IDs for all episodes of passed TV series

Create a file containing the names of the TV series you are interested in. One title per line. Empty lines and lines starting with the hash sign (`#`) are ignored. Example:

my_series.txt:

```
Arrested Development
Six Feet Under
True Detective
# this is a comment
```

Then call:

```
tv-series-find-episode-ids -i my_series.txt -o my_episodes.csv
```

Episode IDs and titles for all the TV series mentioned in `my_series.txt` will be written to `my_episode_ids.csv` like this:

```
2510426;"Title of the episode"
2580386;"Title of the episode"
2639284;"Title of the episode"
2545702;"Title of the episode"
2639288;"Title of the episode"
```

### 2. Download subtitles for passed IMDB IDs

Sign up at [OpenSubtitles.org](https://www.opensubtitles.org/). Consider buying a VIP account, otherwise you will hit the download limit very soon.

Set environment variables `OPENSUB_USER` and `OPENSUB_PASSWD` to contain your OpenSubtitles.org credentials.

```
export OPENSUB_USER='you@example.com'
export OPENSUB_PASSWD='yourpassword'
```

Then call:

```
tv-series-download-subs -i my_episodes.csv -o my_subs/
```

All the episodes's subtitles will be downloaded to the directory `my_subs/` as SRT files.

### 3. Search downloaded subtitles

my_regex.txt:

```
one.*regular expression per line
case insensitive
```

```
tv-series-search-subs -i my_subs/ -p my_regex.txt -o my_matches.csv
```

### 4. Approve matches

```
tv-series-matches-approve -i my_matches.csv -o my_answers.csv
```

### 5. Check all positive answers again

```
tv-series-matches-check-approved -i my_answers.csv -o my_answers_checked.csv
```

### 5. Print all positive answers

```
tv-series-matches-print-approved -i my_answers_checked.csv
```

## Help

Call any of the executables mentioned in [Usage](#usage) with the parameter `-h` or `--help` to see full documentation. Example:

```
tv-series-download-subs -h
```

## Contributing

__Feel free to remix this piece of software.__ See [NOTICE](./NOTICE) and [LICENSE](./LICENSE) for license information.
