# Misskey Very Simple Scheduler

A very simple scheduler for Misskey-based software.
This was made in rush (under an hour) for Momoka and Ranko birthday preparation automated post.
There'll be not much development for this bot type. But can be a way to prepare own's Misskey library
that caters my bot framework.

## Usage

```sh
python app.py
```

## Requirements

- This is tested on Python `3.8`. *It may be able to run on lower versions.*
- `requests` and `pyyaml` library.

## Config File

A config file is a file named either `config.yaml` or `config.yml` (with former takes precedence).

It's structure is simply like this:
```yaml
# map of users available to control
users:
  <user-key>:
    host:  <misskey-host> # such as https://misskey.io, https://misskey.flowers, etc.
    token: <user-token>   # either grab your global account token or API. Highly suggests the latter.
# list of posts scheduled to post
posts:
- user:    <user-key>            # see users part of the config
  time:    <post-unix-timestamp> # at which local time to perform the post (please sync your clock)
  content: <post-content>        # post content
  files:   <post-file-ids>       # post files
  folders: <post-folder-ids>     # post files from folders
- ...
```
