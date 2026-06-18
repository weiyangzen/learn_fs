# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_stdia.c

Read status: complete.

Purpose: stdin-read implementation for platforms with unbuffered `read`.

Main logic:
- `gp_stdin_read` calls `read(fileno(f), buf, len)` directly.

Filesystem/storage relevance:
- Provides low-level unbuffered standard-input reading for file/pipe/console streams.
