# -*- coding: UTF-8 -*-

import os
import sys
import time
import config
import getframe
import getsubtitle


def clear():
    if sys.platform.find("win") > -1:
        os.system("cls")
    else:
        print()


def main():
    conf = config.get_config("", "")

    if not(os.path.exists(conf['video_dir'])):
        os.mkdir(conf['video_dir'])

    if not(os.path.exists(conf['video_frames'])):
        os.mkdir(conf['video_frames'])

    if not(os.path.exists(conf['output_dir'])):
        os.mkdir(conf['output_dir'])

    video_name = ""
    video_suffix = ""

    while True:
        clear()
        print("----------Select Video----------")
        video_list = os.listdir(conf['video_dir'])

        if len(video_list) < 1:
            print("Nothing found\n\n")
            print("Process finished")
            input()
            return

        for video in video_list:
            print("%d.%s" % (video_list.index(video) + 1, video))

        try:
            index = int(input("\nInput index: "))
        except ValueError:
            continue

        if 0 < index <= len(video_list):
            video_name = video_list[index - 1][: video_list[index - 1].rfind(".")]
            video_suffix = video_list[index - 1][video_list[index - 1].rfind("."):]
            break

    start = time.time()
    print("\n----------Video Division----------")
    print("Start video division")

    if not getframe.main(video_name, video_suffix):
        print("Video division FAILED!")
        print("Process finished")
        input()
        return

    print("Video division finished")
    print("Time: %.2fs\n" % (time.time() - start))

    start2 = time.time()
    print("----------Subtitle Analysis----------")
    print("Start subtitle analysis")

    if not getsubtitle.main(video_name, video_suffix):
        print("\nSubtitle analysis FAILED!")
    else:
        print("\nSubtitle analysis finished")

    print("Time: %.2fs\n" % (time.time() - start2))

    print("Process finished")
    print("Time: %.2fs" % (time.time() - start))
    input()
    return


if __name__ == "__main__":
    main()
