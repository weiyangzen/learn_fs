# File Research: sources/os/plan9/plan9/sys/src/cmd/mtime.c

Prints file modification times.

Behavior:
- Usage: `mtime file...`.
- For each path, calls `dirstat()`.
- Prints `mtime` as an unsigned decimal field plus filename.
- Reports stat errors to stderr and exits with `"errors"` if any failed.

This is a small diagnostic command around Plan 9 `Dir.mtime`.
