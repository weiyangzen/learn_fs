# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/alloc.c

Read fully: 23 lines, 286 bytes. SHA-256 prefix: `9a9d5e565ce7dc5c`.

This file provides public memdraw allocation wrappers for the OS X GUI backend.

Functions:
- `allocmemimage()` calls `_allocmemimage()`.
- `freememimage()` calls `_freememimage()`.
- `memfillcolor()` calls `_memfillcolor()`.

Integration: supplies expected libdraw/memdraw symbols while delegating to underscored internal implementations.

Risk notes: no logic beyond direct forwarding.
