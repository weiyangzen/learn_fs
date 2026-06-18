# File Research: sources/os/bsd/openbsd-src/sbin/dump/dumprmt.c

## Purpose
Implements remote tape access for `rdump` using the historical `rmt(8)` protocol over `rcmd()`.

## Key Behavior
- `rmthost()` stores remote host/user, installs a SIGPIPE handler, and opens the remote shell connection.
- `rmtgetconn()` resolves `shell/tcp`, validates optional remote username, calls `rcmd()` to run `_PATH_RMT`, and tunes socket buffers/TCP options.
- `okname()` restricts remote usernames to ASCII alnum, `_`, and `-`.
- `rmtopen()`, `rmtclose()`, `rmtread()`, `rmtwrite()`, `rmtseek()`, and `rmtioctl()` encode protocol commands.
- `rmtreply()` parses `A`, `E`, and `F` replies, maps remote errno, and closes state on fatal replies.
- `rmtgets()` reads newline-terminated protocol response lines byte-by-byte.

## Notes
The code assumes trusted legacy remote-shell semantics and treats protocol desynchronization or connection loss as dump-aborting conditions.
