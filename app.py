from flask import Flask, jsonify, request
import sqlite3
import re
import platform

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/poem/list/sample', methods=['POST'])
def get_sample_poemlist():
    data = request.get_json()
    page = data['page']
    conn = sqlite3.connect('database/poem.db')
    c = conn.cursor()

    columns = ['id', 'title', 'author', 'dynasty', 'abstract', 'comment_count', 'type']
    sql = '''select _id, mingcheng, zuozhe, chaodai, zhaiyao, shipin, 'sample' from poem 
    where chaodai='唐代' order by shipin desc limit 20 offset :offset'''
    assert (len(columns) == len(re.search(r'(?<=select).+(?=from)', sql).group(0).split(',')))

    cursor = c.execute(sql, {'offset': page * 20})
    result = []
    for r in cursor:
        result.append({
            columns[i]: r[i] for i in range(len(columns))
        })
    return jsonify(result)


@app.route('/poem/text', methods=['POST'])
def get_poem_text():
    poem_id = request.get_json()['poem_id']
    conn = sqlite3.connect('database/poem.db')
    c = conn.cursor()

    columns = ['title', 'author_name', 'dynasty', 'text', 'author_abstract']
    sql = '''select p.mingcheng, p.zuozhe, p.chaodai, p.yuanwen, a.jieshao from poem p inner join author a
    on p.zuozhe = a.xingming where p._id = :pid'''
    assert (len(columns) == len(re.search(r'(?<=select).+(?=from)', sql).group(0).split(',')))

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
        app.run(host='0.0.0.0', ssl_context=('/ssl_file/www.hyunee.top.pem', '/ssl_file/www.hyunee.top.key'))
