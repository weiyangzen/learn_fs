# File Research: sources/os/plan9/9front/sys/src/cmd/xargs.c

Small Plan 9 `xargs` implementation that batches input lines into command arguments and runs a limited number of child processes.

Key behavior:
- `-n` controls number of input lines per command, default 10.
- `-p` controls maximum concurrent processes, default 1.
- Reads newline-delimited strings from stdin with `Brdstr()`, appends them after the fixed command argv, forks, and execs.
- If direct exec fails for a non-path command, retries with `/bin/<cmd>`.
- Frees read argument strings in the parent and waits for all children at exit.

Notable dependencies:
- Plan 9 Bio, fork/exec/wait primitives.

Research notes:
- Input splitting is strictly by line; it does not implement shell-like quoting or whitespace splitting.
