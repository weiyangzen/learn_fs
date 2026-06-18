# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_strdl.c

Read status: complete.

Purpose: default stream-based readline implementation.

Main logic:
- `gp_readline_init` returns success without allocating state.
- `gp_readline` delegates to `sreadline`.
- `gp_readline_finit` is a no-op.

Filesystem/storage relevance:
- None directly. It supports interpreter input reading through Ghostscript streams.
