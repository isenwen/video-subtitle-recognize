# -*- coding: UTF-8 -*-

import sys


def get_config(video_name, video_suffix):
    current_path = sys.path[0]

    return {
        # 以下请填写自己的 APP 信息
        'APP_KEY': '282ec2d6c6754b27f010f4d8ee241629',  # 修改为你的 APP_KEY
        'SECRET_KEY': 'aed9fafcd6a77e8ed2ab3786055bb120',  # 修改为你的 SECRET_KEY

        # 以下请根据需要调整数值
        'split_duration': 1,  # 切片间隔，每 split_duration 秒输出一帧
        'jpg_quality': 40,  # 图片输出质量, 0~100
        'probability': 0.66,  # OCR可信度下限, 0~1

        # 以下为目录信息，一般不需要更改
        'video_dir': '%s/video/' % current_path,  # 视频源文件目录
        'video_path': '%s/video/%s%s' % (current_path, video_name, video_suffix),  # 指定视频文件路径
        'video_frames': '%s/video_frames/' % current_path,  # 视频切片文件目录
        'image_dir': '%s/video_frames/%s/' % (current_path, video_name),  # 指定视频切片文件目录
        'output_dir': '%s/output/' % current_path  # 字幕输出目录
    }
