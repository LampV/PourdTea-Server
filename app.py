#! /usr/local/bin/python3
# encoding=utf-8

from flask import Flask, jsonify, request, current_app, g, Response
import sqlite3
import re
import platform
from utils import *
import account
import poem

app = Flask(__name__)


def get_authors():
    with app.app_context():
        authors = current_app.config.get('authors', None)
    if not authors:
        with app.app_context():
            print('fetch authors')
            conn = sqlite3.connect('database/poem.db')
            cursor = conn.cursor()
            cursor.execute('select xingming from author')
            authors = current_app.config['authors'] = [d[0] for d in cursor.fetchall()]
    return authors


@app.before_request
def get_conn():
    conn = sqlite3.connect('database/poem.db')
    g.conn = conn
    g.cursor = conn.cursor()


# TODO 增加自动注册的逻辑
@app.route('/account/login', methods=['POST', 'GET'])
def wx_login():
    """
    通过qq服务器的jscode获取openid，并尝试获取服务器用户信息
    只有注册用户在服务器有信息，因此若有信息说明已经注册，会一起返回
    若没有信息则说明没有注册，通过account_info为空可以判断
    """
    # 获取 openid
    data = request.get_json()
    jscode = data['code']

    openid, session_key = code2session(jscode)

    # 尝试获取account_info
    account_info = account.get_account_info_by_openid(openid, g.cursor)

    return jsonify({'openid': openid, 'account_info': account_info})


@app.route('/account/get_info', methods=['POST'])
def get_info():
    data = request.get_json()
    openid = data['openid']

    # 获取account_info对象
    account_info = account.get_account_info_by_openid(openid, g.cursor)

    return jsonify({'account_info': account_info})


@app.route('/account/like', methods=['POST'])
def change_like_status():
    data = request.get_json()
    action = data['action']
    uid, pid = data['uid'], data['pid']

    # 改变状态
    account.change_poem_status(
        'like', action, uid, pid, g.conn, g.cursor)

    return 'success'


@app.route('/poem/infer/list', methods=['POST'])
def get_infer_poemlist():
    data = request.get_json()
    page, uid = data['page'], data['uid']

    poems = poem.get_infer_poems(uid, page, g.cursor)

    return jsonify(poems)


@app.route('/poem/search/list', methods=['POST'])
def get_search_reault():
    data = request.get_json()
    page, uid = data['page'], data['uid']
    search_content = data['searchContent']

    authors = get_authors()

    if search_content:
        poems = poem.get_search_list(uid, page, search_content, g.cursor, authors)
    else:
        poems = poem.get_poem_list(uid, page, g.cursor)
    return jsonify(poems)


@app.route('/poem/like/list', methods=['POST'])
def get_like_poemlist():
    data = request.get_json()
    uid = data['uid']

    poems = poem.get_like_poems(uid, g.cursor)

    return jsonify(poems)


@app.route('/poem/text', methods=['POST'])
def get_poem_text():
    poem_id = request.get_json()['poem_id']
    conn = sqlite3.connect('database/poem.db')
    c = conn.cursor()

    columns = ['title', 'author_name', 'dynasty', 'text', 'author_abstract']
    sql = '''select p.mingcheng, p.zuozhe, p.chaodai, p.yuanwen, a.jieshao from poem p inner join author a
    on p.zuozhe = a.xingming where p._id = :pid'''
    assert (len(columns) == len(
        re.search(r'(?<=select).+(?=from)', sql).group(0).split(',')))

    cursor = c.execute(sql, {'pid': poem_id})
    result = []
    for r in cursor:
        result.append({
            columns[i]: r[i] for i in range(len(columns))
        })
    return jsonify(result[0])  # 注意返回原文并不需要列表


if __name__ == '__main__':
    if platform.system() == 'Drawin':  # Mac上说明是测试环境
        app.run()
    else:  # 否则都认为是正式环境
        app.run(host='0.0.0.0', ssl_context=(
            '/ssl_file/3894881_www.hyunee.top.pem', '/ssl_file/3894881_www.hyunee.top.key'))
