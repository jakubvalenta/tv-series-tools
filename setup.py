from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tv_series_tools',
    version='1.1.0',
    description='Tools to work with TV series\'s subtitles.',
    long_description=long_description,
    url='https://lab.saloun.cz/jakub/tv-series-tools',
    author='Jakub Valenta',
    author_email='jakub@jakubvalenta.cz',
    license='Apache Software License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Artistic Software',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
    ],
    keywords='',
    packages=find_packages(),
    install_requires=[
        'requests',
        'imdbpy',
        'python-opensubtitles',
        'pysrt',
        'termcolor',
        'moviepy',
    ],
    entry_points={
        'console_scripts': [
            'tv-series-download-subs='
            'tv_series.download_subs:download_subs_and_cache_results',
            'tv-series-find-episode-ids='
            'tv_series.find_episode_ids:find_and_write_episode_ids',
            'tv-series-search-subs='
            'tv_series.search_subs:search_subs_and_save_matches',
            'tv-series-matches-approve='
            'tv_series.approve_matches:approve_matches_and_save_answers',
            'tv-series-matches-check-approved='
            'tv_series.approve_matches:check_positive_answers',
            'tv-series-matches-print-approved='
            'tv_series.approve_matches:print_positive_answers',
        ]
    },
)
