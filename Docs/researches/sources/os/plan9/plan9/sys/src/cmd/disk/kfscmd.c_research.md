# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfscmd.c

This standalone utility sends commands to a running KFS command service.

Key behavior:
- Parses optional `-n server` to select `/srv/kfs.<name>.cmd`; otherwise opens `/srv/kfs.cmd`.
- Writes each command argument to the command fd.
- Reads command output until it sees `done`, `success`, or `unknown command`.
- Prints command output to stdout and tracks command errors.
- Exits with `"errors"` if any command failed.

Role:
- Operator-facing client for the command channel implemented by `main.c`/`con.c`.
