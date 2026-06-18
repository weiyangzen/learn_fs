# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_stdin.c

Read status: complete.

Purpose: portable stdin-read implementation for platforms without unbuffered read support.

Main logic:
- `gp_stdin_read` uses `fread`.
- If `interactive` is nonzero, reads at most one byte.
- Otherwise reads up to `len` bytes.

Filesystem/storage relevance:
- Standard-input abstraction for portable builds.

Notable behavior:
- Comments note it is slow for stdin because interactive reads are byte-at-a-time.
