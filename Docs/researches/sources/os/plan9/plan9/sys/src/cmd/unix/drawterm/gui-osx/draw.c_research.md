# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/draw.c

Read fully: 22 lines, 365 bytes. SHA-256 prefix: `ab2e1a1b8e32dfc6`.

This file provides OS X GUI backend wrappers around internal memdraw drawing helpers.

Functions:
- `memimagedraw()` calls `_memimagedrawsetup()` and passes the result to `_memimagedraw()`.
- `pixelbits()` delegates to `_pixelbits()`.
- `memimageinit()` delegates to `_memimageinit()`.

Integration: bridges public memdraw-style symbols to underscored internal implementations for the drawterm OS X GUI library.

Risk notes: direct forwarding only; correctness depends entirely on the internal memdraw implementation.
