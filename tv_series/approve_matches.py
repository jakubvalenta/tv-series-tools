import math
import re
import sys

import listio
from termcolor import colored

from tv_series import common


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


def add_subs_context_to_matches(matches, no=1):
    for match in matches:
        subs = common.read_subs(match['file_path'])
        if subs is None:
            continue
        for i, sub in enumerate(subs):
            sub_match = common.convert_sub_to_match(match['file_path'], sub)
            if sub_match != match:
                continue
            match['subs_context'] = find_subs_context(subs, i, no)
            yield match


def format_sub_match_with_context(match, color=True, i=None, total=None):
    if color:
        file_path_formatted = colored(match['file_path'], attrs=('bold',))
    else:
        file_path_formatted = match['file_path']

    if i is not None:
        if total is not None:
            index_formatted = '{}/{} '.format(i, total)
        else:
            index_formatted = '{} '.format(i)
    else:
        index_formatted = ''

    return(
        '\n'
        '{index_formatted}'
        '{file_path} {time_start} --> {time_end}\n'
        '\n'
        '{subs_context}\n'
        '\n'
        .format(
            file_path=file_path_formatted,
            time_start=match['time_start'],
            time_end=match['time_end'],
            subs_context=common.format_subs(match['subs_context'], color),
            index_formatted=index_formatted
        )
    )


def approve_matches(matches, totals=False):
    if totals:
        matches = list(matches)
        total = len(matches)
    else:
        total = None
    for i, match in enumerate(matches):
        print(format_sub_match_with_context(match, i=i+1, total=total))

        inp = None
        while inp is None or (inp not in ('y', 'n', 'x', '') and
                              not re.match(r'^\d{1,2}$', inp)):
            print('Do you like this match? "y" = yes, "n" or nothing = no,'
                  ' "?" = ask again next time, "AB" start at line number A and'
                  ' end at B')
            inp = input('--> ')

        if inp == '?':
            continue
        if inp in ('', 'y', 'n'):
            if inp == '':
                yes_or_no = 'n'
            else:
                yes_or_no = inp
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
            common.parse_sub_time(match['subs_context'][i_start].start),
            common.parse_sub_time(match['subs_context'][i_end].end)
        )


def filter_approved_answers(answers):
    return (
        answer
        for answer in answers
        if answer[0] == 'Y'
    )


def filter_not_answered_matches(matches, answer_matches):
    for match in matches:
        if match in answer_matches:
            print('ALREADY ANSWERED "{f}" {s} --> {e}'.format(
                f=match['file_path'],
                s=match['time_start'],
                e=match['time_end']))
            continue
        yield match


def approve_matches_and_save_answers():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Check matches and save answers'
    )
    parser.add_argument('--input', '-i', dest='inputfile', required=True,
                        help='path to a file with the matches')
    parser.add_argument('--output', '-o', dest='outputfile', required=True,
                        help='path to a file in which the answers will be'
                        ' stored')
    parser.add_argument('--totals', '-t', dest='totals', action='store_true',
                        help='show total number of matches to answer,'
                        ' this will cause that if there are a lot of matches'
                        ' it will take quite a lot of time before the first'
                        ' question shows up')
    args = parser.parse_args()

    matches_list = listio.read_map(args.inputfile)
    matches = (common.convert_list_to_match(l) for l in matches_list)
    answers = listio.read_map(args.outputfile)
    # Using list instead of generator so that we can read it several times.
    matches_answered = [convert_answer_to_match(answer) for answer in answers]
    matches_not_answered = filter_not_answered_matches(
        matches,
        matches_answered
    )
    matches_with_context = add_subs_context_to_matches(matches_not_answered, 2)
    answers = approve_matches(matches_with_context, totals=args.totals)

    listio.write_map(args.outputfile, answers)

    sys.exit()


def check_positive_answers():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Check again positive answers'
    )
    parser.add_argument('--input', '-i', dest='inputfile', required=True,
                        help='path to a file with the answers')
    parser.add_argument('--output', '-o', dest='outputfile', required=True,
                        help='path to a file in which the new answers will be'
                        ' stored')
    args = parser.parse_args()

    answers = listio.read_map(args.inputfile)
    approved = filter_approved_answers(answers)
    matches = (convert_answer_to_match(answer) for answer in approved)
    matches_with_context = add_subs_context_to_matches(matches, 3)
    new_answers = approve_matches(matches_with_context)

    listio.write_map(args.outputfile, new_answers)

    sys.exit()


def print_positive_answers():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Print positive answers with context'
    )
    parser.add_argument('--input', '-i', dest='inputfile', required=True,
                        help='path to a file with the answers')
    args = parser.parse_args()

    answers = listio.read_map(args.inputfile)
    approved = filter_approved_answers(answers)
    matches = (convert_answer_to_match(answer) for answer in approved)
    matches_with_context = add_subs_context_to_matches(matches, 3)
    (
        print(format_sub_match_with_context(match, color=False))
        for match in matches_with_context
    )

    sys.exit()


if __name__ == '__main__':
    approve_matches_and_save_answers()
