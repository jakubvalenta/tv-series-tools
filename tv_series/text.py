#!/usr/bin/env python

from moviepy.editor import *

from tv_series import common


SIZE = (1280, 720)
DURATION = 3
FPS = 24


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Text'
    )
    parser.add_argument('--input', '-i', dest='inputfile', required=True,
                        help='input file')
    args = parser.parse_args()

    inp = common.read_list_from_file(args.inputfile, False)

    for file_path, text in inp:
        text_clip = TextClip(text, color='white', font="Arial", fontsize=48)
        composite_clip = CompositeVideoClip(
            [text_clip.set_pos('center')],
            size=SIZE
        )
        final_clip = composite_clip.subclip(0, DURATION)
        final_clip.write_videofile(file_path, fps=FPS, codec='png')


if __name__ == '__main__':
    main()
