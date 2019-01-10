"""
DATE NER EXPERIMENT
"""

import re
from datetime import datetime, timedelta
import time
from dateutil.parser import parse
import jieba.posseg as psg

def time_extract(text):
#对句子进行解析，提取其中所有能表示日期时间的词，并进行上下文拼接
    time_res = []
    raw_word = ''
    word = ''
    keyDate = {'今天': 0, '明天': 1, '后天': 2}
    for k, v in psg.cut(text):
        if k in keyDate:
            time_res.append(word)
            word = (datetime.today() + timedelta(days=keyDate.get(k,
                0))).strftime('%Y年%m月%d日')
            raw_word = k
        elif word !='':
            if v in ['m', 't']:
                word = word + k
                raw_word = raw_word + k
            else:
                time_res.append(word)
                word = ''
                raw_word = ''
        elif v in ['m', 't']:
            word = k
            raw_word = k
    if word != '':
        time_res.append(word)
    result = list(filter(lambda x: x is not None, [check_time_valid(w) for w in
        time_res]))
    print(result)
    final_res = [parse_datetime(w) for w in result]    
    return [x for x in final_res if x is not None]


def check_time_valid(word):
# 对提取的拼接日期串进行进一步处理，以进行有效性判断。    
    m = re.match("\d+$", word)
    if m:
        if len(word) <=6:
            return None
    word1 = re.sub('[号|日]\d+$', '日', word)
    if word1 !=word:
        return check_time_valid(word1)
    else:
        return word1


def parse_datetime(msg):
#将提取的文本日期串进行时间转换
    if msg is None or len(msg) == 0:
        return None

    try:
        dt = parse(msg, fuzzy=False)
        print("待转换字符串："+msg)
        print(dt)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        m = re.match(
                r"([0-9零一二两三四五六七八九十]+年)?([0-9零一二两三四五六七八九十]+月)?([0-9零一二两三四五六七八九十]+[号日])?([上中下午晚早]+)?([0-9零一二两三四五六七八九十百]+[点:\.时])?([0-9零一二两三四五六七八九十百]+分?)?([0-9零一二两三四五六七八九十百]+秒)?", msg)
    if m.group(0) is not None:
        res = {
                "year": m.group(1),
                "month": m.group(2),
                "day": m.group(3),
                "hour": m.group(5) if m.group(5) is not None else '00',
                "minute": m.group(6) if m.group(6) is not None else '00',
                "second": m.group(7) if m.group(7) is not None else '00',
                }
        if res["minute"][-1]!='分':
            res["minute"] += '分'
        if res["second"][-1]!='秒':
            res["second"] += '秒'
        params = {}
        for name in res:
            if res[name] is not None and len(res[name]) != 0:
                tmp = None
                if name == 'year':
                    tmp = year2dig(res[name][:-1])
                else:
                    tmp = cn2dig(res[name][:-1])
                if tmp is not None:
                    params[name] = int(tmp)
        target_date = datetime.now().replace(**params)
        is_pm = m.group(4)
        if is_pm is not None:
            if is_pm == u'下午' or is_pm == u'晚上' or is_pm ==u'中午':
                hour = target_date.time().hour
                if hour < 12:
                    target_date = target_date.replace(hour = hour + 12)
        return target_date.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None


UTIL_CN_NUM = {
        '零': 0, '一': 1, '二':2, '两': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七':7, '八': 8, '九': 9,
        '0' : 0, '1' : 1, '2' :2, '3' : 3, '4' : 4,
        '5' : 5, '6' : 6, '7' :7, '8' : 8, '9' : 9
}

UTIL_CN_UNIT = {'十' : 10, '百' : 100, '千' : 1000, '万' : 10000}


def cn2dig(src):
    if src == "":
        return None
    m = re.match("\d+", src)
    if m:
        return int(m.group(0))
    rsl = 0
    unit = 1
    for item in src[::-1]:
        if item in UTIL_CN_UNIT.keys():
            unit = UTIL_CN_UNIT[item]
        elif item in UTIL_CN_NUM.keys():
            num = UTIL_CN_NUM[item]
            rsl += num * unit
        else:
            return None
    if rsl < unit:
        rsl += unit
    return rsl


def year2dig(year):
    res = ''
    for item in year:
        if item in UTIL_CN_NUM.keys():
            res = res +str(UTIL_CN_NUM[item])
        else:
            res = res + item
    m = re.match("\d+", res)
    if m:
        if len(m.group(0))==2:
            return int(datetime.datetime.today().year/100)*100 + int(m.group(0))
        else:
            return int(m.group(0))
    else:
        return None



if __name__ == '__main__':
    text0 = '今天是几号？'
    print(text0, time_extract(text0), sep=':')

    text1 = '我要住到明天下午三点十五'
    print(text1, time_extract(text1), sep=':')

    text2 = '预订28号的房间'
    print(text2, time_extract(text2), sep=':')

    text3 = '我要从26号下午4点住到2月二号'
    print(text3, time_extract(text3), sep=':')

    text4 = '我要预订今天到30号的房间'
    print(text4, time_extract(text4), sep=':')
