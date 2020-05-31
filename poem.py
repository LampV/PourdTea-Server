#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@author: Jiawei Wu
@create time: 2020-05-15 22:34
@edit time: 2020-05-31 21:02
@FilePath: /vpoem/poem.py
@desc: 
"""
import re
from utils import *

poem_require_fields = [
    'pid', 'title', 'author', 'dynasty', 'abstract', 'comment_count', 'like_flag',
    'theme'
]
poem_rename_dict = {
    'pid': 'poem._id',
    'title': 'mingcheng',
    'author': 'zuozhe',
    'dynasty': 'chaodai',
    'abstract': 'zhaiyao',
    'theme': 'fenlei',
    'comment_count': 'shipin',
    'like_flag': 'l.uid',
}

text_require_fields = [
    'pid', 'title', 'author_name', 'dynasty', 'text', 'author_abstract', 'like_flag'
]
text_rename_dict = {
    'pid': 'p._id',
    'title': 'p.mingcheng',
    'author_name': 'p.zuozhe',
    'dynasty': 'p.chaodai',
    'text': 'p.yuanwen',
    'author_abstract': 'a.jieshao',
    'like_flag': 'l.uid',
}

poem_require_fields_str = get_require_str(poem_require_fields, poem_rename_dict)
text_require_fields_str = get_require_str(text_require_fields, text_rename_dict)


def get_poem_text(poem_id, uid, cursor):
    """获取古诗原文，以对象数组形式返回"""
    text_select_sql = '''
        SELECT {}
          FROM poem p
          INNER JOIN author a
          LEFT JOIN account_likes l on p._id = l.pid AND l.uid=?
          LEFT JOIN account_favors f on p._id = f.pid AND f.UID=?
        '''.format(text_require_fields_str)

    cursor.execute(text_select_sql, (poem_id, uid))

    result = cursor.fetchone()

    detail = {key: value for key, value in zip(
        text_require_fields, result)}

    return detail


def get_poem_list(uid, page, cursor):
    """
    获取PAGE_SIZE数量的读书笔记，并以对象数组的形式返回
    :param page:    页码
    :param cursor:  句柄
    :return:
    """

    poem_select_sql = '''
        SELECT {}
          FROM poem
          LEFT JOIN account_likes l on poem._id = l.pid AND l.uid=?
          LEFT JOIN account_favors f on poem._id = f.pid AND f.UID=?
        ORDER BY poem.shipin DESC LIMIT ? OFFSET (?) 
        '''.format(poem_require_fields_str)
    cursor.execute(poem_select_sql, (uid, uid, PAGE_SIZE, page * PAGE_SIZE))

    results = cursor.fetchall()

    poems = [{key: value for key, value in zip(
        poem_require_fields, result)} for result in results]

    for poem in poems:
        poem['searchContent'] = ''

    return poems


def get_infer_poems(uid, page, cursor):
    """
    获取PAGE_SIZE数量的读书笔记，并以对象数组的形式返回
    :param page:    页码
    :param cursor:  句柄
    :return:
    """

    poem_select_sql = '''
        SELECT {}
          FROM poem
          LEFT JOIN account_likes l on poem._id = l.pid AND l.uid=?
          LEFT JOIN account_favors f on poem._id = f.pid AND f.UID=?
          ORDER BY poem._id DESC LIMIT ? OFFSET (?) 
        '''.format(poem_require_fields_str)
    cursor.execute(poem_select_sql, (uid, uid, PAGE_SIZE, page * PAGE_SIZE))
    results = cursor.fetchall()

    poems = [{key: value for key, value in zip(
        poem_require_fields, result)} for result in results]

    for poem in poems:
        poem['searchContent'] = 'infer'

    return poems


def get_like_poems(uid, cursor):
    poem_select_sql = '''
    SELECT {}
      FROM account_likes l
      INNER JOIN poem ON l.pid = poem._id
      INNER JOIN account ON l.uid = account.id
      WHERE l.uid=?
      ORDER BY l.add_date DESC
    '''.format(poem_require_fields_str)

    cursor.execute(poem_select_sql, (uid,))
    results = cursor.fetchall()

    poems = [{key: value for key, value in zip(
        poem_require_fields, result)} for result in results]

    for poem in poems:
        poem['searchContent'] = 'like'

    return poems


def get_search_list(uid, page, content, cursor, authors):
    dynasies = ['先秦', '战国', '汉', '魏晋', '隋', '唐', '周', '五代',
                '南唐', '辽', '宋', '元', '明', '清', '近代', '现代', '未知']
    themes = ['写景', '咏物', '春天', '夏天', '秋天', '冬天', '写雨', '写雪', '写风', '写花', '梅花', '荷花',
              '菊花', '柳树', '月亮', '山水', '写山', '写水', '长江', '黄河', '儿童', '写鸟', '写马', '田园',
              '边塞', '地名', '节日', '春节', '元宵', '寒食', '清明', '端午', '七夕', '中秋', '重阳', '怀古',
              '抒情', '爱国', '离别', '送别', '思乡', '思念', '爱情', '励志', '哲理', '闺怨', '悼亡', '写人',
              '老师', '母亲', '友情', '战争', '读书', '惜时', '忧民', '婉约', '豪放', '民谣']
    # 如果内容被朝代包含
    if re.sub(r'[朝代]', '', content) in dynasies:
        poems = get_poems_by_classifier(
            uid, page, 'chaodai', re.sub(r'[朝代]', '', content), cursor)
    elif content in themes:
        poems = get_poems_by_classifier(uid, page, 'fenlei', content, cursor)
    elif content in authors:
        poems = get_poems_by_classifier(uid, page, 'zuozhe', content, cursor)
    else:
        poems = get_poems_by_intelligent(uid, page, content, cursor)

    return poems


def get_poems_by_classifier(uid, page, classifier, content, cursor):
    poem_select_sql = '''
         SELECT {}
          FROM poem
          LEFT JOIN account_likes l on poem._id = l.pid AND l.UID=?
          LEFT JOIN account_favors f on poem._id = f.pid AND f.UID=?
          WHERE {}='{}' 
          ORDER BY poem._id DESC LIMIT ? OFFSET (?) 
        '''.format(poem_require_fields_str, classifier, content)

    cursor.execute(poem_select_sql, (uid, uid, PAGE_SIZE, page * PAGE_SIZE,))
    results = cursor.fetchall()

    poems = [{key: value for key, value in zip(
        poem_require_fields, result)} for result in results]

    for poem in poems:
        poem['searchContent'] = content

    return poems


def get_poems_by_intelligent(uid, page, content, cursor):
    """只返回20条结果"""
    if page > 0:
        return []
    poem_select_sql = '''
        SELECT {poem_require_fields_str}
          FROM poem
            LEFT JOIN account_likes l on poem._id = l.pid AND l.UID={uid}
            LEFT JOIN account_favors f on poem._id = f.pid AND f.UID={uid}
          WHERE mingcheng like '%{content}%'
        UNION
        SELECT {poem_require_fields_str}
          FROM poem
            LEFT JOIN account_likes l on poem._id = l.pid AND l.UID={uid}
            LEFT JOIN account_favors f on poem._id = f.pid AND f.UID={uid}
          WHERE zhaiyao like '%{content}%'
        UNION
        SELECT {poem_require_fields_str}
          FROM poem
            LEFT JOIN account_likes l on poem._id = l.pid AND l.UID={uid}
            LEFT JOIN account_favors f on poem._id = f.pid AND f.UID={uid}
          WHERE yuanwen like '%{content}%'
        ORDER BY shipin DESC LIMIT 20
        '''.format(poem_require_fields_str=poem_require_fields_str, uid=uid, content=content)

    cursor.execute(poem_select_sql)
    results = cursor.fetchall()

    poems = [{key: value for key, value in zip(
        poem_require_fields, result)} for result in results]
    for poem in poems:
        poem['searchContent'] = content

    poems.sort(key=lambda p: p['comment_count'], reverse=True)

    return poems
