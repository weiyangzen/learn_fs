# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass4.c

This file implements phase 4: reference count checking and clearing of unresolved inodes.

Key behavior:
- Iterates all allocated inode-state entries by cylinder group.
- Clears zero-link files/directories when no references remain.
- For valid files and connected directories, calls `adjust()` when residual link count is nonzero.
- Clears disconnected directories left in `DSTATE`.
- Clears `DCLEAR` and `FCLEAR` inodes as zero-length, bad, or duplicate, except when already handled for snapshots.
- Leaves `USTATE` untouched.

Important interactions:
- Uses `freeblock` descriptor callbacks for inode clearing.
- Consumes link-count residuals built by pass 2 and connectivity state built by pass 3.
- Calls `clri()` and `adjust()` from shared repair code.
