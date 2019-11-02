from flask import Flask
import sqlite3
import re

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/poem/list/sample')
def get_sample_poemlist():
    conn = sqlite3.connect('poem.db')
    c = conn.cursor()

    columns = ['id', 'title', 'author', 'dynasty', 'abstract', 'type']
    sql = '''select _id, mingcheng, zuozhe, chaodai, zhaiyao, shipin, 'sample' from poem 
    where chaodai='唐代' order by shipin desc limit 20'''
    assert (len(columns) == len(re.search(r'(?<=select).+(?=from)', sql).group(0).split(',')))

    cursor = c.execute(sql)
    result = []
    for r in cursor:
        result.append({
            columns[i]: r[i] for i in range(len(columns))
        })


if __name__ == '__main__':
    app.run()
