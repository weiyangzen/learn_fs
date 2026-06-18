# File Research: sources/os/plan9/plan9/sys/src/9/boot/aux.c

Common boot utility routines.

Key behavior:
- `warning()` and `fatal()` report boot errors; `fatal()` exits with a message, causing kernel panic in boot context.
- `readfile()`/`writefile()` provide small whole-file helpers.
- `setenv()` writes to `#e`.
- `srvcreate()` posts an fd into `#s` under the basename of the requested service name.
- `catchint()` handles alarm notes for timed prompts.
- `outin()` prompts with a default value, optionally timing out under CPU-server boot mode.

Commented-out legacy `plumb()`/`sendmsg()` code is present but inactive.
