# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/cload.c

Read fully: 10 lines, 188 bytes. SHA-256 prefix: `cd64e127ed8664bf`.

This file provides the OS X GUI backend wrapper for compressed image loading.

Single function:
- `cloadmemimage()` delegates to `_cloadmemimage()` with the same image, rectangle, data pointer, and byte count.

Integration: exposes the expected memdraw API name for code linked against this GUI backend.

Risk notes: no validation or transformation is performed here.
