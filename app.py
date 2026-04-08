#!/usr/bin/env python3
import json
import time
import yaml
import pathlib
from datetime import datetime
import requests

users = {}
posts = []

def load_config():
  global users, posts
  data = None
  for config_file in ('config.yaml', 'config.yml'):
    path = pathlib.Path.cwd() / config_file
    if not path.exists():
      continue
    data = yaml.load(path.read_text(), Loader=yaml.Loader)
    break

  if not data:
    raise RuntimeError('config files not found. cannot start program')

  users = data['users']
  posts = data['posts']

def process_post(post):
  user = users.get(post['user'])
  session = requests.Session()
  if not user:
    return
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
      folder_files.sort(key=lambda f: datetime.strptime(
        f['createdAt'],
        r'%Y-%m-%dT%H:%M:%S.%f%z',
      ).timestamp())
      files.extend(f['id'] for f in folder_files)

  if len(files) > 16:
    print('There are {} files found, exceeds software limit (16). Truncating the rest.'.format(len(files)))

  session.post('{}/api/notes/create'.format(user['host']), json={
    'i': user['token'],
    'text': post['content'],
    'fileIds': files[:16],
  })

def main():
  while True:
    ctime = time.time()
    rest_posts = [p for p in posts if ctime <= p['time']]
    post_times = list(set(p['time'] for p in rest_posts))
    if not post_times:
      print('No more posts to process. Exiting.')
      break
    ntime = post_times[0]
    next_posts = [p for p in posts if abs(ntime - p['time']) <= 1e-6]

    ctime = time.time()
    time.sleep(ntime - ctime)
    for post in next_posts:
      process_post(post)

load_config()

if __name__ == '__main__':
  main()
