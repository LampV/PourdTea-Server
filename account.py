#! /usr/local/bin/python3
# encoding=utf-8

import requests
import json
from utils import *

def get_account_info(identify, id_type, cursor):
    """
    通过openid获取用户信息
    :param identify: 用户身份标识
    :param id_type: 标识类型, str in ["openid", "id"]
    :param cursor: 数据库句柄
    :return: dict类型的account_info
    """
    require_fields = [
        'uid'
    ]
    rename_dict = {
        'uid': 'id'
    }
    require_fields_str = get_require_str(require_fields, rename_dict)

    select_sql = '''
            SELECT {}
              FROM account
              WHERE {}=(?)
            '''.format(require_fields_str, id_type)

    cursor.execute(select_sql, (identify,))
    result = cursor.fetchone()

    # 叫做account_info 是为了和qq的user_info 做区分
    account_info = {key: value for key, value in zip(require_fields, result)} if result else None

    return account_info


def get_account_info_by_openid(openid, cursor):
    """
    通过openid获取用户信息，若没有则注册
    :param cursor: 数据库句柄
    :param openid: openid
    :return: dict类型的account_info
    """

    account_info = get_account_info(openid, 'openid', cursor)
    if not account_info: # 若没有则注册
        add_account(openid, cursor.connection, cursor)
        account_info = get_account_info(openid, 'openid', cursor)
    return account_info


def get_account_info_by_uid(uid, cursor):
    """
    uid
    :param cursor: 数据库句柄
    :param uid: uid
    :return: dict类型的account_info
    """
    return get_account_info(uid, 'id', cursor)


def add_account(openid, conn, cursor):
    """
    添加一条account信息
    :param user_info:   QQ用户信息
    :param openid:      用户在小程序的唯一标识
    :param school:      用户学校
    :param conn:        数据库连接
    :param cursor:      连接句柄
    :return:
    """
    insert_sql = '''
        INSERT INTO account (openid) VALUES (?) 
        '''
    cursor.execute(insert_sql, (openid, ))
    conn.commit()
    return 'success'


def change_poem_status(status, action, uid, pid, conn, cursor):
    """
    用户对笔记的喜欢/收藏状态改变，需要修改数据库内容，包括：
    1. 在用户和笔记的关系表中增加/删除行
    2. 受到影响的笔记的喜欢数/收藏数会变化
    :param status:  需要改变的状态是：like/favor
    :param action:  具体的动作是 True/False -> 确认或取消
    :param uid:
    :param pid:
    :param conn:
    :param cursor:
    :return:
    """
    # 如果action是True，则执行增加操作
    if action:
        if status == 'like':
            insert_sql = '''INSERT INTO account_likes (uid, pid) VALUES (?, ?) ON CONFLICT DO NOTHING '''
        else:
            insert_sql = '''INSERT INTO account_favors (uid, pid) VALUES (?, ?)  ON CONFLICT DO NOTHING '''
        cursor.execute(insert_sql, (uid, pid))
    # 否则执行删除操作
    else:
        if status == 'like':
            delete_sql = '''DELETE FROM account_likes WHERE (uid, pid)=(?, ?)'''
        else:
            delete_sql = '''DELETE FROM account_favors WHERE (uid, pid)=(?, ?)'''
        cursor.execute(delete_sql, (uid, pid))

    conn.commit()
    return 'success'
