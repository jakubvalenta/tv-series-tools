import math

import pysrt
from termcolor import colored


def parse_sub_text(s):
    return s.replace('\n', ' ')


def parse_sub_time(t):
    return t.ordinal / 1000


def convert_seconds_to_subriptime(t):
    milliseconds = t * 1000
    return pysrt.SubRipTime(milliseconds=milliseconds)


def convert_sub_to_match(file_path, sub):
    return {
        'file_path': file_path,
        'time_start': parse_sub_time(sub.start),
        'time_end': parse_sub_time(sub.end),
    }


def convert_list_to_match(l):
    return {
        'file_path': l[0],
        'time_start': float(l[1]),
        'time_end': float(l[2]),
    }


def convert_match_to_list(match):
    return (
        match['file_path'],
        match['time_start'],
        match['time_end'],
    )


def read_subs(file_path):
    try:
        return pysrt.open(file_path)
    except UnicodeDecodeError:
        print(colored('ERROR Failed to parse "{}"'.format(file_path), 'red'))
        return None


def get_sub_at(subs, seconds):
    milliseconds = seconds * 1000
    srttime = pysrt.SubRipTime(milliseconds=milliseconds + 1)
    all_subs_at_time = subs.at(srttime)
    if len(all_subs_at_time):
        return all_subs_at_time[0]
    return None


def format_sub_time(srttime):
    return '{:02d}:{:02d}:{:02d}'.format(
        srttime.hours,
        srttime.minutes,
        srttime.seconds
    )


def format_subs(subs, color=True):
    if type(subs) != tuple and type(subs) != list:
        subs = [subs]
    middle = math.floor(len(subs) / 2)
    formatted = []
    for i, sub in enumerate(subs):
        no = i - middle
        if no == 0 and color:
            text = colored(sub.text, 'blue')
        else:
            text = sub.text
        formatted.append('{no}  {text:<80} {start} --> {end}'.format(
            no=abs(no),
            text=parse_sub_text(text),
            start=format_sub_time(sub.start),
            end=format_sub_time(sub.end)
        ))
    return '\n'.join(formatted)
