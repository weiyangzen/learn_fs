# File Research: sources/os/plan9/9front/sys/src/cmd/upas/q/qer.c

Queues a mail delivery job into the upas queue directory.

Key responsibilities:
- Creates per-user queue directory under a queue root.
- Creates a temporary data file `D.XXXXXX` and writes stdin into it.
- Copies optional associated files supplied by `-f` into `F...` queue files.
- Creates a locked control file `C...` containing description, reply-to, argument list, and associated files.
- Supports `-q dir` for explicit queue subdirectory, with broader permissions when queueing as `none`.

Filesystem relevance:
- Queue job is represented by matching `C.*`, `D.*`, optional `F*` files.
- Uses `mktemp()`, `create()`, `syscreatelocked()`, and `sysunlockfile()`.
- Directory/file permissions vary based on user or queue-dir mode.

Notable quirks:
- Logs if the first data chunk does not begin with `From`.
- The read error on stdin is commented out and not fatal.
