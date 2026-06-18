# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/errstr.h

Maps `ext2srv` internal error enum values from `dat.h` to human-readable 9P error strings.

Key behavior:
- Defines `errmsg[]` with designated entries for format errors, I/O failures, permission failures, missing filesystem devices, no space, corrupt filesystem, and unclean filesystem state.
- `xfssrv.c` exposes these strings through `xerrstr()`.

Risks and invariants:
- The array must remain aligned with the error enum in `dat.h`.
- Unknown enum values fall back to `no such error` in `xerrstr()`.
