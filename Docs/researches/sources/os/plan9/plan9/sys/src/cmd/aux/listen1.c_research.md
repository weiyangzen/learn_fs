# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/listen1.c

This file implements a one-address listener that runs a supplied command per connection.

Key behavior:
- Announces a given network address.
- Optionally becomes user `none` unless trusted mode is selected.
- Accepts each call in a child process.
- Binds the connection's data file to `/dev/cons`, dup's the accepted fd to stdio, and execs the command.
- Optionally prints verbose call information.

Important details:
- Supports `-t` trusted and `-v` verbose.
- Falls back to executing `/bin/<cmd>` if direct exec fails.

Filesystem relevance:
- Indirect: service launcher built around Plan 9 network connection files.
