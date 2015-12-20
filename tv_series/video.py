import math
import os
import sys

from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip

from tv_series import common


DEFAULT_LIMIT = -1
DEFAULT_FPS = 24
DEFAULT_EXT = '.avi'
DEFAULT_DIR = 'clips'

VIDEO_FORMAT_SIZE_W = 640
VIDEO_FORMAT_SIZE_H = 360

DEBUG_SKIP = ()


def render(clip, file_path, fps=None, ext=None):
    if fps is None:
        fps = DEFAULT_FPS
    if ext is None:
        ext = DEFAULT_EXT
    base, _ = os.path.splitext(file_path)
    if ext == '.avi':
        codec = 'png'
    clip.write_videofile(base + ext, fps=fps, codec=codec)


def subtitle_generator(txt):
    return TextClip(txt, font='Georgia-Regular', fontsize=24, color='white')


def parse_duration(duration):
    return duration.replace(',', '.')


def format_duration(duration):
    return duration.replace(':', '_').replace('.', '_')


def format_clip_file_path(file_path, cut_start, cut_end):
    file_dir, file_basename = os.path.split(file_path)
    file_name, file_ext = os.path.splitext(file_basename)
    new_path_without_ext = os.path.join(file_dir, DEFAULT_DIR, file_name)
    return '{path}-{start}-{end}{ext}'.format(
        path=new_path_without_ext,
        start=format_duration(cut_start),
        end=format_duration(cut_end),
        ext=file_ext
    )


def create_super_cut():
    import argparse

    parser = argparse.ArgumentParser(
        description='TV Series Tools: Video'
    )
    parser.add_argument('--input', '-i', dest='inputfile', required=True,
                        help='file path to a file containing info on how to'
                        ' cut the clips')
    parser.add_argument('--output', '-o', dest='outputfile', required=True,
                        help='output video file path')
    parser.add_argument('--clips', '-c', dest='clipsdir', required=True,
                        help='clips video files location')
    parser.add_argument('--join', '-j', dest='join', action='store_true',
                        help='concat cut video clips')
    parser.add_argument('--change-fps', '-f', dest='change_fps', type=int,
                        default=DEFAULT_FPS,
                        help='video fps')
    parser.add_argument('--resize-width', '-rw', dest='resize_width',
                        type=int,
                        help='resize width; you must set both --resize-width'
                        ' and --resize-height')
    parser.add_argument('--resize-height', '-rh', dest='resize_height',
                        type=int,
                        help='resize height; you must set both --resize-width'
                        ' and --resize-height')
    parser.add_argument('--limit', '-l', dest='limit', type=int,
                        default=DEFAULT_LIMIT,
                        help='process only first <limit> clips')
    parser.add_argument('--speed', '-s', dest='speed', type=float,
                        help='speed of the composition; the standard speed'
                        ' will be multiplied by this number, hence'
                        ' 1 = normal speed, 0.5 = half the normal speed,'
                        ' 3 = three times as fast, etc.')
    args = parser.parse_args()

    inp = common.read_list_from_file(args.inputfile, False)
    if not inp:
        sys.exit(1)

    video_clips = {}
    all_clips = []

    i = 0
    for file_name, start, end in inp:
        if i == args.limit:
            break
        i = i + 1

        file_path = os.path.join(args.clipsdir, file_name)
        subtitles_path = os.path.splitext(file_path)[0] + '.srt'
        cut_start = parse_duration(start)
        cut_end = parse_duration(end)
        print(
            'CLIP {}\n'
            '  {}\n'
            '  {}\n'
            '  {} --> {}'
            .format(
                i,
                file_path,
                subtitles_path,
                cut_start,
                cut_end
            )
        )
        if file_name in DEBUG_SKIP:
            print('  SKIP')
            continue
        if not args.join:
            clip_file_path = format_clip_file_path(file_path, cut_start, cut_end)
            if os.path.isfile(clip_file_path):
                print('  SKIP EXISTS')
                continue
        if not os.path.isfile(file_path):
            print('  SKIP FILE NOT FOUND')
            continue

        if file_path not in video_clips:
            video_clips[file_path] = VideoFileClip(file_path)
        video_clip = video_clips[file_path]
        video_sub_clip = video_clip.subclip(
            cut_start,
            cut_end
        )
        if args.change_fps:
            video_sub_clip = video_sub_clip.set_fps(args.change_fps)
        if args.resize_width and args.resize_height:
            video_sub_clip = video_sub_clip.resize(width=args.resize_width, height=args.resize_height)
        #subtitles_clip = SubtitlesClip(
        #    subtitles_path,
        #    subtitle_generator
        #)
        composite_clip = video_sub_clip
        #composite_clip = CompositeVideoClip([video_sub_clip, subtitles_clip])
        #composite_clips.append(composite_clip)

        if args.speed is not None:
            # composite_clip = composite_clip.speedx(factor=args.speed)
            pass

        if args.join:
            all_clips.append(composite_clip)
        else:
            render(composite_clip, clip_file_path, fps=args.change_fps)

    if args.join:
        joined_clip = concatenate_videoclips(all_clips)
        render(joined_clip, args.outputfile, fps=args.change_fps)

    sys.exit()


if __name__ == '__main__':
    create_super_cut()
