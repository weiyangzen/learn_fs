# File Research: sources/os/plan9/plan9/sys/src/9/port/auth.c

This file implements selected authentication and identity syscalls/helpers.

Key responsibilities:
- Stores global `eve` and `hostdomain`.
- `iseve` tests whether the current user is the host owner.
- `sysfversion` negotiates a 9P version on a file descriptor by calling `mntversion`.
- `sys_fsession` is a deprecated compatibility stub.
- `sysfauth` performs mount authentication through `mntauth` and returns a close-on-exec auth fd.
- `userwrite` allows switching to user `"none"`.
- `hostownerwrite` changes host owner and current user, restricted to `eve`.
- `hostdomainwrite` updates host domain, restricted to `eve`.

Filesystem/storage relevance:
- 9P mount versioning and authentication affect remote filesystem access.
- Identity checks feed file permission behavior in generic device and namespace code.
