# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-factotum.c

POSIX support for user and factotum discovery.

Functions:
- `getuser` returns the passwd database name for `getuid`, or `"none"`.
- `nsfromdisplay` derives a namespace path from `$DISPLAY`, canonicalizing `:0.0` to `:0`.
- `getns` uses `$NAMESPACE` or the display-derived namespace.
- `dialfactotum` connects to the Unix-domain socket `<namespace>/factotum` and returns it as a Plan 9 fd via `lfdfd`.

Notable behavior:
- Undefines POSIX wrappers for `socket`, `connect`, `getenv`, and `access`.
- Intended for hosted drawterm integration with plan9port-style factotum sockets.
