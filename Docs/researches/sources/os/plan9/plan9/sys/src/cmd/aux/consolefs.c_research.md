# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/consolefs.c

This file implements `consolefs`, a 9P filesystem presenting configured serial consoles as files.

Key behavior:
- Reads console definitions from `/lib/ndb/consoledb` or a configured NDB file.
- Exposes a one-level namespace with up to three files per console: data, `ctl`, and `stat`.
- Opens serial devices, configures baud rate, and launches a reader process per active console.
- Broadcasts console output to all open data fids using per-fid circular buffers and delayed read replies.
- Writes to data files go to the console device, except `/dev/null` "chat" consoles broadcast user-tagged messages.

Important details:
- Supports open-on-demand consoles that close when no client is attached.
- Access control is based on `uid`/`gid` fields in the NDB console entry.
- Directory entries are generated dynamically from configured consoles and existing control/status fds.
- Flush removes pending read requests by tag.
- Mounts through a pipe and posts `#s/consoles`.

Filesystem relevance:
- Direct: full user-level 9P filesystem for multiplexing and controlling console devices.
