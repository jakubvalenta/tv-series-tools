import math
import os
import re
import readline
import sys

import pysrt
from termcolor import colored

from tv_series import common


def parse_sub_text(s):
    return s.replace('\n', ' ')


def parse_sub_time(t):
    return t.ordinal / 1000


def convert_sub_to_match(file_path, sub):
    return {
        'file_path': file_path,
        'time_start': parse_sub_time(sub.start),
        'time_end': parse_sub_time(sub.end),
    }


def convert_match_to_answer(match, yes_or_no, start, end):
    return (
        yes_or_no.upper(),
        match['file_path'],
        match['time_start'],
        match['time_end'],
        start,
        end,
    )


def convert_answer_to_match(answer):
    return {
        'file_path': answer[1],
        'time_start': float(answer[2]),
        'time_end': float(answer[3]),
    }


def find_subs_context(subs, current, no=1):
    context = []
    for i in range(current - no, current + no + 1):
        if i < 0 or i >= len(subs):
            continue
        context.append(subs[i])
    return context


def compile_regex(pattern):
    return re.compile(pattern, flags=re.IGNORECASE)


def search_line(line, regex_list):
    for i, regex in enumerate(regex_list):
        m = regex.search(line)
        if m:
            return True
    return False


def read_subs(file_path):
    try:
        return pysrt.open(file_path)
    except UnicodeDecodeError:
        print('ERROR Subtitle file "{}" could not be read.'.format(file_path))
        return None


def iter_subs(dir_path):
    d = os.scandir(dir_path)
    for entry in sorted(d, key=lambda entry: entry.name):
        if entry.name.startswith('.'):
            continue
        if entry.is_dir():
            for ret in iter_subs(entry.path):
                yield ret
            continue
        if not entry.is_file() or not entry.name.endswith('.srt'):
            continue
        subs = read_subs(entry.path)
        if subs is not None:
            yield (entry.path, subs)


def search_subs(subs_dir, excl, regex_list):
    for file_path, subs in subs_dir:
        for i, sub in enumerate(subs):
            match = convert_sub_to_match(file_path, sub)
            if match in excl:
                print('ANSWERED', match)
                continue
            line = parse_sub_text(sub.text)
            if not search_line(line, regex_list):
                continue
            subs_context = find_subs_context(subs, i, 2)
            yield {
                'file_path': match['file_path'],
                'time_start': match['time_start'],
                'time_end': match['time_end'],
                'subs_context': subs_context,
            }


def format_subs(subs, color=True):
    if type(subs) != tuple and type(subs) != list:
        subs = [subs]
    middle = math.floor(len(subs) / 2)
    formatted = []
    for i, sub in enumerate(subs):
        no = i - middle
        if no == 0 and color:
            text = colored(sub.text, 'red')
        else:
            text = sub.text
        formatted.append('{no}  {text:<80} {start} --> {end}'.format(
            no=abs(no),
            text=parse_sub_text(text),
            start='{:02d}:{:02d}:{:02d}'
            .format(sub.start.hours, sub.start.minutes, sub.start.seconds),
            end='{:02d}:{:02d}:{:02d}'
            .format(sub.end.hours, sub.end.minutes, sub.end.seconds),
        ))
    return '\n'.join(formatted)


def format_sub_match_with_context(match, color=True):
    if color:
        file_path_formatted = colored(match['file_path'], attrs=('bold',))
    else:
        file_path_formatted = match['file_path']
    return(
        '\n'
        '{file_path} {time_start} --> {time_end}\n'
        '\n'
        '{subs_context}\n'
        '\n'
        .format(
            file_path=file_path_formatted,
            time_start=match['time_start'],
            time_end=match['time_end'],
            subs_context=format_subs(match['subs_context'], color)
        )
    )


def approve_matches(matches):
    for match in matches:
        print(format_sub_match_with_context(match))

        inp = None
        while inp is None or (inp not in ('y', 'n', 'x', '') and
                              not re.match(r'^\d{1,2}$', inp)):
            print('Do you like this match? "y" = yes, "n" = no, "x" = ask'
                  ' again next time, "AB" start at line number A and end at B')
            inp = input('--> ')

        if inp in ('', 'x'):
            continue
        if inp in ('y', 'n'):
            yes_or_no = inp.upper()
            no_start = 0
            no_end = no_start
        elif len(inp) == 1:
            yes_or_no = 'y'
            no_start = int(inp)
            no_end = no_start
        else:
            yes_or_no = 'y'
            no_start = -1 * int(inp[0])
            no_end = int(inp[1])

        i_middle = math.floor(len(match['subs_context']) / 2)
        i_start = i_middle + no_start
        i_end = i_middle + no_end
        yield convert_match_to_answer(
            match,
            yes_or_no,
            parse_sub_time(match['subs_context'][i_start].start),
            parse_sub_time(match['subs_context'][i_end].end)
        )


def filter_approved_answers(answers):
    for answer in answers:
        if answer[0] == 'Y':
            yield answer


def add_subs_context_to_matches(matches, no=1):
    for match in matches:
        subs = read_subs(match['file_path'])
        if subs is None:
            continue
        for i, sub in enumerate(subs):
            sub_match = convert_sub_to_match(match['file_path'], sub)
            if sub_match != match:
                continue
            match['subs_context'] = find_subs_context(subs, i, no)
            yield match


def search_and_approve_subs():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Search subtitles'
    )
    parser.add_argument('--input', '-i', dest='inputdir', required=True,
                        help='path to a directory with the subtitle SRT files')
    parser.add_argument('--output', '-o', dest='outputfile', required=True,
                        help='path to a file in which the answers will be'
                        ' stored')
    parser.add_argument('--patterns', '-p', dest='patterns', required=True,
                        help='path to a file with search patterns')
    args = parser.parse_args()

    excl = [
        convert_answer_to_match(answer)
        for answer in common.read_list_from_file(args.outputfile, False)
    ]
    regex_list = [
        compile_regex(pattern)
        for pattern in common.read_list_from_file(args.patterns)
    ]
    subs_dir = iter_subs(args.inputdir)
    matches_with_context = search_subs(subs_dir, excl, regex_list)
    answers = approve_matches(matches_with_context)

    common.write_list_to_file(args.outputfile, answers)

    sys.exit()


def check_approved_subs():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Check approved subtitles'
    )
    parser.add_argument('--input', '-i', dest='inputfile', required=True,
                        help='path to a file with the answers')
    parser.add_argument('--output', '-o', dest='outputfile', required=True,
                        help='path to a file in which the new answers will be'
                        ' stored')
    args = parser.parse_args()

    answers = common.read_list_from_file(args.inputfile, False)
    approved = filter_approved_answers(answers)
    matches = [convert_answer_to_match(answer) for answer in approved]
    matches_with_context = add_subs_context_to_matches(matches, 3)
    new_answers = approve_matches(matches_with_context)

    common.write_list_to_file(args.outputfile, new_answers)

    sys.exit()


def print_approved_subs():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Print answers with context'
    )
    parser.add_argument('--input', '-i', dest='inputfile', required=True,
                        help='path to a file with the answers')
    args = parser.parse_args()

    answers = common.read_list_from_file(args.inputfile, False)
    approved = filter_approved_answers(answers)
    matches = [convert_answer_to_match(answer) for answer in approved]
    matches_with_context = add_subs_context_to_matches(matches, 3)
    [
        print(format_sub_match_with_context(match, False))
        for match in matches_with_context
    ]

    sys.exit()


if __name__ == '__main__':
    seach_and_approve_subs()
