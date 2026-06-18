# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/errstr.h

Definitions of Plan 9-style error string globals for the VNC compatibility layer.

Key contents:
- Defines string storage for all errors declared in `error.h`.
- Covers mount, path, permission, I/O, descriptor, process, memory, mouse, stat, and miscellaneous error messages.

Role:
- Provides address-stable global strings so code can pass symbolic error variables to `error()`.

Risks:
- It is a `.h` containing definitions, so it should be included in exactly one C translation unit; here `compat.c` includes it.
