#!/usr/bin/env python3
import time
import yaml
import pathlib
from datetime import datetime
import requests

from typing import List, Dict, Any

users : Dict[str, Dict[str, Any]] = {}
posts : List[Dict[str, Any]] = []

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

class WorkingPost:
  def __init__(self, post):
    self.user    = users[post['user']]
    self.post    = post
    self.session = requests.Session()

    self.files = []

  def fetch_files(self):
    if self.post.get('files'):
      self.files.extend(self.post['files'])
    if self.post.get('folders'):
      for folder_id in self.post['folders']:
        folder_files = self.session.post('{}/api/drive/files'.format(self.user['host']), json={
          'i': self.user['token'],
          'folderId': folder_id,
          'limit': 16,
          'sinceId': '0',
          'sort': None,
        }).json()
        folder_files.sort(key=lambda f: datetime.strptime(
          f['createdAt'],
          r'%Y-%m-%dT%H:%M:%S.%f%z',
        ).timestamp())
        self.files.extend(f['id'] for f in folder_files)

  def post_note(self):
    if len(self.files) > 16:
      print('There are {} files found, exceeds software limit (16). Truncating the rest.'.format(len(self.files)))

    # NOTE: /i/registry doesn't work properly with API Token
    #       because misskey source code states that every provided API token
    #       (non-global/internal one) are forced to access their own
    #       scope part of the registry.
    #       One of the reason that "reactionAcceptance" is not synced
    #       through Misskey clients.
    self.session.post('{}/api/notes/create'.format(self.user['host']), json={
      'i': self.user['token'],
      'text': self.post['content'],
      'fileIds': self.files[:16],
    })

  def __enter__(self):
    return self

  def __exit__(self, *exc):
    return False

def process_post(post):
  if post['user'] not in users:
    return

  with WorkingPost(post) as wp:
    wp.fetch_files()
    wp.post_note()

def process_fetch_only(post):
  if post['user'] not in users:
    return

  with WorkingPost(post) as wp:
    wp.fetch_files()

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
