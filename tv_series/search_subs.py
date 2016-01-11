import os
import re
import sys

import listio
from termcolor import colored

from tv_series import common


def compile_regex(pattern):
    return re.compile(pattern, flags=re.IGNORECASE)


def search_line(line, regex_list):
    for i, regex in enumerate(regex_list):
        m = regex.search(line)
        if m:
            return True
    return False


def iter_subs_files(dir_path):
    d = os.scandir(dir_path)
    for entry in sorted(d, key=lambda entry: entry.name):
        if entry.name.startswith('.'):
            continue
        if entry.is_dir():
            for file_path in iter_subs_files(entry.path):
                yield file_path
            continue
        if not entry.is_file() or not entry.name.endswith('.srt'):
            continue
        file_path = os.path.abspath(entry.path)
        print('READING "{}"'.format(file_path))
        yield file_path


def search_subs(paths_and_subs, excl, regex_list):
    for file_path, subs in paths_and_subs:
        for sub in subs:
            match = common.convert_sub_to_match(file_path, sub)
            if match in excl:
                print('ALREADY PROCESSED "{f}" {s} --> {e}'.format(
                    f=match['file_path'],
                    s=match['time_start'],
                    e=match['time_end']))
                continue
            line = common.parse_sub_text(sub.text)
            if not search_line(line, regex_list):
                continue
            else:
                print(colored(
                    'MATCHED "{f}" {s} --> {e}'.format(
                        f=match['file_path'],
                        s=match['time_start'],
                        e=match['time_end']),
                    'green'))
                yield match


def read_subs(paths):
    for file_path in paths:
        subs = common.read_subs(file_path)
        if subs:
            yield (file_path, subs)


def search_subs_and_save_matches():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Search subtitles'
    )
    parser.add_argument('--input', '-i', dest='inputdir', required=True,
                        help='path to a directory with the subtitle SRT files')
    parser.add_argument('--output', '-o', dest='outputfile', required=True,
                        help='path to a file in which the matches will be'
                        ' stored')
    parser.add_argument('--patterns', '-p', dest='patterns', required=True,
                        help='path to a file with search patterns')
    args = parser.parse_args()

    excl = [
        common.convert_list_to_match(match)
        for match in listio.read_map(args.outputfile)
    ]
    regex_list = [
        compile_regex(pattern)
        for pattern in listio.read_list(args.patterns)
    ]
    paths = iter_subs_files(args.inputdir)
    subs = read_subs(paths)
    matches = search_subs(subs, excl, regex_list)
    matches_list = (
        common.convert_match_to_list(match)
        for match in matches
    )

    listio.write_map(args.outputfile, matches_list)

    sys.exit()


if __name__ == '__main__':
    search_subs_and_save_matches()
