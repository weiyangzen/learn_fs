# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbcreate.c

This command creates mailboxes or folders for the current user.

Key behavior:
- Usage: `mbcreate [-f] ...`.
- Default operation calls `creatembox(getuser(), name)`.
- With `-f`, calls `createfolder(getuser(), name)`.
- Accumulates errors across all arguments and exits `errors` if any creation fails.

Integration and risks:
- Creation semantics and permissions are in `common/libsys.c`.
