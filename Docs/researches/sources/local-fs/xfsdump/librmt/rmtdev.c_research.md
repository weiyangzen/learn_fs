# File Research: sources/local-fs/xfsdump/librmt/rmtdev.c

Implements `_rmt_dev(path)`.

Behavior:
- A path is considered remote only if it contains a colon followed by `/dev/`.
- Returns 1 for remote, 0 otherwise.

Important distinction:
- `rmtopen()` treats any path containing `:` as remote, while `_rmt_dev()` is stricter and only recognizes `:/dev/`.
