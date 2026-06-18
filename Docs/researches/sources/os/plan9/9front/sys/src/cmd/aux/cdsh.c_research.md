# File Research: sources/os/plan9/9front/sys/src/cmd/aux/cdsh.c

Role: Minimal interactive shell for choosing a directory under an optional root.

Behavior:
- Supports only `cd`, `lc`, and `exit`.
- `-r root` confines navigation under an absolute root by chdiring to root and then to the requested relative path.
- On EOF or exit, prints the final current directory.

Implementation:
- `cd` builds and cleans absolute paths, verifies by performing real `chdir` calls, and restores the previous directory on failure.
- `system` forks `/bin/rc -c` for `lc`.
- `lc ARG` rejects shell metacharacters before synthesizing an `lc ARG` command.

Use case:
- Small helper for interactive directory selection without exposing a general shell.
