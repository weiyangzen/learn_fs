# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/sys.c

Provides error-aware wrappers around basic file-descriptor operations.

Key functions:
- `resetsys` clears the reentrant error guard.
- `syserror` prints operation context, converts the current error string to `Eio`, and avoids recursive error storms.
- `Read` requires an exact byte count; on short read it marks `lastfile` rescuing, reports, calls `rescue`, and exits.
- `Write` requires an exact write count and reports `write` errors through `syserror`.
- `Seek` wraps `seek` and reports failure through `syserror`.

Behavior notes:
- Read failure is considered fatal and triggers rescue rather than returning partial data.
- `inerror` prevents recursive `syserror` handling.
