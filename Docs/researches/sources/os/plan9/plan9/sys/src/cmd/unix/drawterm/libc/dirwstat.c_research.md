# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirwstat.c

This file writes `Dir` metadata to a path.

Key behavior:
- `dirwstat` serializes a `Dir` using `convD2M` and calls `wstat`.

Important details:
- Pathname counterpart to `dirfwstat`.
