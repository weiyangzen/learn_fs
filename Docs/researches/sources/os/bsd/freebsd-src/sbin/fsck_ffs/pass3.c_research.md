# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass3.c

This file implements phase 3: directory connectivity repair.

Key behavior:
- Walks cached directories in reverse sorted order.
- Skips root and already-connected directories.
- Leaves unreferenced soft-updates directories for pass 4 clearing when preen/background state is otherwise resolved.
- Follows parent chains to find the top orphan in a disconnected chain.
- Reconnects orphan directories into `lost+found` with `linkup()`.
- Detects orphaned directory loops and offers reconnection.
- For loops, finds the directory name in its parent, links the orphan, clears the old entry, and adjusts link counts.
- Calls `check_dirdepth()` and `propagate()` after reconnecting.

Important interactions:
- Depends on parent/dotdot information collected in pass 2.
- Uses `linkup()` from `dir.c`, `findname()` / `clearentry()` callbacks from `inode.c`, and directory state from `inoinfo()`.
