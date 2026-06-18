# File Research: sources/os/plan9/plan9/sys/src/cmd/mount.c

Implements Plan 9 `mount`.

Behavior:
- Usage: `mount [-a|-b] [-cnq] [-k keypattern] /srv/service dir [spec]`.
- Opens service file read-write, optionally authenticates with `p9any`, then calls `mount()`.
- Flags map to mount options: `MAFTER`, `MBEFORE`, `MCREATE`, `MCACHE`.
- `-n` disables authentication.
- `-q` suppresses errors and exits success on open/mount failure.
- Optional `spec` defaults to empty string when argc is 2.

Key functions:
- `amount0()` performs `fauth`, `auth_proxy`, and `mount`.
- `catch()` reports notes and exits.
- `usage()` prints syntax.

Notes:
- Rejects combining `-a` and `-b`.
- Uses global `keyspec`.
