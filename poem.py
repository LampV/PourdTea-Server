#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@author: Jiawei Wu
@create time: 2020-05-15 22:34
@edit time: 2020-05-15 23:24
@FilePath: /vpoem/poem.py
@desc: 
"""
from utils import *
poem_require_fields = [
    'pid', 'title', 'author', 'dynasty', 'abstract', 'comment_count', 'like_flag'
]
poem_rename_dict = {
    'pid': 'poem._id',
    'title': 'mingcheng',
    'author': 'zuozhe',
    'dynasty': 'chaodai',
    'abstract': 'zhaiyao',
    'comment_count': 'shipin',
    'like_flag': 'l.uid',
}
poem_require_fields_str = get_require_str(poem_require_fields, poem_rename_dict)


def get_poem_list(page, dynasty, author, cursor):
    """
    获取PAGE_SIZE数量的读书笔记，并以对象数组的形式返回
    :param page:    页码
    :param cursor:  句柄
    :return:
    """

    poem_select_sql = '''
        SELECT {}
          FROM poem
          LEFT JOIN account_likes l on poem._id = l.pid
          LEFT JOIN account_favors f on poem._id = f.pid
        '''.format(poem_require_fields_str) + \
          (''' where chaodai={} '''.format(dynasty) if dynasty else '') + \
          (''' where zuozhe={} '''.format(author) if author else '') + \
        ''' ORDER BY poem.shipin DESC LIMIT ? OFFSET (?) '''
    cursor.execute(poem_select_sql, (PAGE_SIZE,
                                     page * PAGE_SIZE,))
    results = cursor.fetchall()

    poems = [{key: value for key, value in zip(
        poem_require_fields, result)} for result in results]

    return poems


def get_infer_poems(page, cursor):
    """
    获取PAGE_SIZE数量的读书笔记，并以对象数组的形式返回
    :param page:    页码
    :param cursor:  句柄
    :return:
    """

    poem_select_sql = '''
        SELECT {}
          FROM poem
          LEFT JOIN account_likes l on poem._id = l.pid
          LEFT JOIN account_favors f on poem._id = f.pid
          ORDER BY poem._id DESC LIMIT ? OFFSET (?) 
        '''.format(poem_require_fields_str)
    cursor.execute(poem_select_sql, (PAGE_SIZE,
                                     page * PAGE_SIZE,))
    results = cursor.fetchall()

    poems = [{key: value for key, value in zip(
        poem_require_fields, result)} for result in results]

    return poems


def get_like_poems(uid, cursor):
    poem_select_sql = '''
    SELECT {}
      FROM account_likes
      INNER JOIN poem ON account_likes.pid = poem._id
      INNER JOIN account ON account_likes.uid = account.id
      LEFT JOIN account_likes l on poem._id = l.pid 
      LEFT JOIN account_favors f on poem._id = f.pid
      WHERE account_likes.uid=?
      ORDER BY account_likes.add_date DESC
    '''.format(poem_require_fields_str)

    cursor.execute(poem_select_sql, (uid, ))
    results = cursor.fetchall()

    poems = [{key: value for key, value in zip(
        poem_require_fields, result)} for result in results]

    return poems
