# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirfwstat.c

This file writes `Dir` metadata to an open fd.

Key behavior:
- `dirfwstat` serializes a `Dir` using `convD2M` and calls `fwstat`.

Important details:
- Allocates exactly `sizeD2M(d)` bytes for the packed stat.
