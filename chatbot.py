import sqlite3
import json
from datetime import datetime

connection = sqlite3.connect('2015-01.db')
c = connection.cursor()

def create_table():
    c.execute(
        'create table if not exists parent_reply(parent_id text primary key, comment_id text unique, parent text, comment text, subreddit text, unix int, score int)'
    )

def format_data(data):
    data = data.replace('\n', " newlinechar ").replace('\r', " newlinechar ").replace('"', "'")
    return data

create_table()
rc = 0
pr = 0

with open('E:/Django/DATA_SET/RC_2015-01', buffer=1000)as f:
    for row in f:
        rc+=1
        row = json.loads(row)
        parent_id = row['parent_id']
        body = format_data(row['body'])
        created_utc = row['created_utc']
        score = row['score']
        subreddit = row['subreddit']

        parent_data = find
