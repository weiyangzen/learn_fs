# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/main.c

Provides the `hjfs` program entry point, global errors, allocation helpers, daemon startup, periodic sync, and shutdown.

Key points:
- Defines common error strings used by the filesystem implementation.
- Provides fatal allocation wrappers `emalloc`, `erealloc`, and `estrdup` with malloc/realloc tags.
- `getthrdata` lazily allocates thread-local response state and a response channel.
- `dprint` prefixes debug output with `hjfs:`.
- `syncproc` calls `sync(0)` periodically at `SYNCINTERVAL`.
- `threadmain` parses options:
  - `-A` enables authentication by clearing `FSNOAUTH`.
  - `-r` reams the filesystem.
  - `-S` disables permission checks and allows chown.
  - `-s` serves over stdio.
  - `-f` selects backing device/file.
  - `-n` sets service name.
  - `-m` sets buffer memory budget.
  - `-a` adds announce addresses.
- Initializes the buffer cache, backing device, filesystem, console, sync process, and 9P service.
- `shutdown` write-locks the filesystem, syncs twice, logs, and exits all threads.

Dependencies and interactions:
- Calls `bufinit`, `newdev`, `initfs`, `initcons`, `start9p`, and `sync`.
- Uses Plan 9 thread and process primitives.

Research relevance:
- This file defines how `hjfs` is configured and launched, including reaming, serving mode, authentication/permission flags, and shutdown durability behavior.
