# File Research: sources/teaching/xv6-public/cat.c

User-space `cat` utility.

Behavior:
- Reads from stdin when no file arguments are supplied.
- Otherwise opens each file read-only, streams it to fd 1 in 512-byte chunks, and closes it.
- Exits on open, read, or write errors with a diagnostic.

This is a minimal syscall exercise for `open`, `read`, `write`, `close`, and `exit`.
