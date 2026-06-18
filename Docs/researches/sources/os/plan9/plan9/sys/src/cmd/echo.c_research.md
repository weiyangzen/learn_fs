# File Research: sources/os/plan9/plan9/sys/src/cmd/echo.c

Simple `echo` command.

Key behavior:
- Supports `-n` to suppress trailing newline.
- Builds one output buffer from arguments separated by spaces.
- Writes once to fd 1 and reports write errors to stderr.

Filesystem relevance:
- Minimal command I/O; no filesystem-specific logic beyond stdout/stderr writes.
