from flask import Flask, jsonify, request
import sqlite3
import re

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/poem/list/sample', methods=['POST'])
def get_sample_poemlist():
    data = request.get_json()
    page = data['page']
    conn = sqlite3.connect('poem.db')
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


if __name__ == '__main__':
    app.run()
