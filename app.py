#!/usr/bin/env python3
import json
import time
import yaml
import datetime
import requests

users = {}
posts = []

def load_config():
  global users, posts
  data = yaml.load(open('config.yaml').read(), Loader=yaml.Loader)
  users = data['users']
  posts = data['posts']

def main():
  while True:
    ctime = time.time()
    rest_posts = [p for p in posts if ctime <= p['time']]
    post_times = list(set(p['time'] for p in posts))
    if not post_times:
      break
    ntime = post_times[0]
    next_posts = [p for p in posts if abs(ntime - p['time']) <= 1e-6]

    ctime = time.time()
    time.sleep(ntime - ctime)
    for post in next_posts:
      user = users.get(post['user'])
      session = requests.Session()
      if not user:
        continue
      files = []
      if post.get('files'):
        files.extend(post['files'])
      if post.get('folders'):
        for folder_id in post['folders']:
          folder_files = session.post('{}/api/drive/files'.format(user['host']), json={
            'i': user['token'],
            'folderId': folder_id,
            'limit': 16,
            'sinceId': '0',
            'sort': None,
          }).json()
          # folder_files.sort(key=lambda f: f)
          files.extend(f['id'] for f in folder_files)
      session.post('{}/api/notes/create'.format(user['host']), json={
        'i': user['token'],
        'text': post['content'],
        'fileIds': files,
      })

load_config()

if __name__ == '__main__':
  main()
