# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/plumber.c

Main entry point and common allocation/error helpers for the plumber daemon.

Key responsibilities:
- Parses `-p` alternate rules file.
- Initializes `$user`, `$home`, and default `$home/lib/plumbing` rule path.
- Reads and parses rules.
- Starts the filesystem service in a separate proc so the main thread can return.
- Provides `error`, `parseerror`, `emalloc`, `erealloc`, and `estrdup`.

Important behavior:
- `parseerror()` prints input stack context, unwinds parser input, stores `lasterror`, and longjmps to `parsejmp`.
- `makeports()` declares ports from parsed rules before mounting the filesystem.

Dependencies:
- Uses Plan 9 threads, auth/fcall/plumb libraries, and globals declared in `plumber.h`.

Notable risks:
- Environment variables `user` and `home` are mandatory.
- Errors call `threadexitsall`, terminating all plumber activity.
