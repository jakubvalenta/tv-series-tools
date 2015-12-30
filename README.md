# TV Series Tools

- Download subtitles for all TV series episodes.
- Search subtitles for specific dialogues and create transcript for [videogrep](https://github.com/antiboredom/videogrep).

## Installation

This software requires Python 2.7. See [Pythons's website](https://www.python.org/) for installation instructions.

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
```

Or you can install this software as a Python package, which will also install all the dependencies and make the executables available globally:

```
python2 setup.py install

tv-series-download-subs -h
tv-series-find-episode-ids -h
```

## Usage

This software works in two phases:

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
tv-series-find-episode-ids -i my_series.txt -o my_episode_ids.txt
```

Episode IDs for all the TV series mentioned in `my_series.txt` will be written to `my_episode_ids.txt` like this:

```
2510426
2580386
2639284
2545702
2639288
```

### 2. Download subtitles for passed IMDB IDs

Sign up at [OpenSubtitles.org](https://www.opensubtitles.org/). Consider buying a VIP account, otherwise you will hit the download limit very soon.

Set environment variables `OPENSUB_USER` and `OPENSUB_PASSWD` to contain your OpenSubtitles.org credentials.

```sh
export OPENSUB_USER='you@example.com'
export OPENSUB_PASSWD='yourpassword'
```

Then call:

```
tv-series-download-subs -i my_episode_ids.txt -o my_subs/
```

All the episodes's subtitles will be downloaded to the directory `my_subs/` as SRT files.

## Help

Call any of the scripts mentioned in [Usage](#usage) with the parameter `-h` or `--help` to see full documentation. Example:

```
tv-series-download-subs -h
```

## Contributing

__Feel free to remix this piece of software.__ See [NOTICE](./NOTICE) and [LICENSE](./LICENSE) for license information.
