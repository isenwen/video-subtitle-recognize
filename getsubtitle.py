# -*- coding: UTF-8 -*-

import os
import re
import difflib
import time
import ocrapi
import config


def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()


def is_image(f):
    return re.match(r'.+jpg', f)


def get_ocr(image_name):
    image = get_file_content(conf['image_dir'] + image_name)
    res = ocrapi.jd_general_ocr(image, conf)
    code = int(res['code'])
    if code != 10000:
        if code in [10043, 10044]:  # 达到OPS上限
            return res['msg'], "QPS Limit"
        return res['msg'], res['code']  # 系统级错误
    else:
        code = int(res['result']['code'])
        if code == 0:
            return res['result']['resultData'], "OK"
        elif code == 13004:
            return res['result']['message'], "No Content"  # 无内容被识别
        else:
            return res['result']['message'], res['result']['code']  # 业务级错误


def main(video_name, video_suffix):
    start = time.time()
    global conf
    conf = config.get_config(video_name, video_suffix)
    output = open(conf['output_dir'] + video_name + '.txt', mode='w')
    probability = conf['probability']
    frames = sorted(filter(is_image, os.listdir(conf['image_dir'])))
    length = len(frames)
    count = 1
    position_data = []

    output.write('----------逐帧OCR结果----------\n\n')

    for image_name in frames:
        output.write(image_name + '\n')
        ocr_result, status = get_ocr(image_name)

        # Fail then retry
        while status == "QPS Limit":
            print(('%s failed for QPS limit, retry...... process: %d%%' %
                   (image_name, (count * 100) // length)).ljust(60, ' '), end='\r')
            time.sleep(0.1)  # 线程暂停避免触发QPS限制
            ocr_result, status = get_ocr(image_name)

        if status != "OK" and status == "No Content":
            output.write('passed (nothing recognized)\n\n')
            print(('%s passed (nothing recognized), process: %d%%' %
                   (image_name, (count * 100) // length)).ljust(60, ' '), end='\r')
            count += 1
            time.sleep(0.1)  # 线程暂停避免触发QPS限制
            continue
        elif status != "OK":
            print(('%s FAILED! Error code: %s' % (image_name, status)).ljust(60, ' '))
            print('Check config / image info, and review document')
            output.close()
            return False

        for word in ocr_result:
            if float(word['probability']) < probability:
                output.write('passed (lower than probability limit)\n')
                continue

            top = int(word['location']['y'])
            height = int(word['location']['height'])
            w = word['text']
            has = False

            for group in position_data:
                # Belong to this group
                if abs(group['top'] - top) < (group['height'] / 2):

                    # Avoid duplicate: check if current word is similar to last word
                    last_word = group['words'][len(group['words']) - 1]

                    if difflib.SequenceMatcher(None, last_word, w).quick_ratio() > 0.8:
                        break

                    # Append words
                    group['words'].append(w)

                    # Cal new value
                    group['totalTop'] += top
                    group['totalHeight'] += height
                    group['totalNum'] += 1
                    group['top'] = group['totalTop'] / group['totalNum']
                    group['height'] = group['totalHeight'] / group['totalNum']
                    has = True
                    break

            if not has:
                position_data.append({
                    'top': top,  # Group standard, using average value of tops
                    'totalTop': top,
                    'height': height,
                    'totalHeight': height,
                    'totalNum': 1,  # How many pics has been add to this group
                    'words': [w]
                })

            output.write('Words: ' + w + '\n')
            output.write('Top: ' + str(word['location']['y']) + '\n')
            output.write('Height: ' + str(word['location']['height']) + '\n')

        count += 1
        output.write('\n\n')
        print(('%s finished, process: %d%%' % (image_name, (count * 100) // length)).ljust(60, ' '), end='\r')
        time.sleep(0.1)  # 线程暂停避免触发QPS限制

    output.write('----------OCR分析信息----------\n\n')

    for group in position_data:
        output.write(str(group) + '\n')

    max_group = []

    for group in position_data:
        if group['totalNum'] > len(max_group): max_group = group['words']

    all_words = ','.join(max_group)

    output.write('\n----------字幕分析结果----------\n\n')
    output.write(all_words + '\n\n')

    output.write('----------程序运行时间----------\n\n')
    end = time.time()
    output.write('Running time: %.2fs' % (end - start) + '\n')

    output.close()
    return True
