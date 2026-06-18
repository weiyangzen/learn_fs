# File Research: sources/os/plan9/9front/sys/src/cmd/troff/popen.c

Read completely: 153 lines, 3271 bytes.

Local `popen`/`pclose` implementation for Plan 9 stdio. It forks `/bin/rc -c <file>`, connects a pipe to the child depending on read/write mode, tracks child pid by file descriptor, and waits for completion.

Key behavior:
- `_pipefd` wraps a pipe fd in a `FILE *`.
- `popen` supports modes beginning with `r` or `w`.
- Child duplicates pipe end to stdin or stdout, closes pipe fds, and execs `/bin/rc`.
- `pclose` closes the stream, waits for the tracked pid, and handles interrupted waits with a note handler.

Reliability notes:
- Tracks by `fileno(fp)` in a fixed `Maxfd` table.
- Reports “no child process for fd” if `pclose` is called on an untracked stream.
