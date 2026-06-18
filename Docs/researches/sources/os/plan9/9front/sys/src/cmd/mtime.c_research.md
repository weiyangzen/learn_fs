# File Research: sources/os/plan9/9front/sys/src/cmd/mtime.c

Small utility that prints modification times for files.

Behavior:
- Usage: `mtime file...`.
- Rejects all options.
- For each argument, calls `dirstat`.
- Prints the file mtime as an unsigned decimal field plus the path.
- Reports stat errors to stderr and exits with `"errors"` if any file failed.

This is a straightforward Plan 9 metadata inspection command.
