# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_lookup.c

Purpose: Implements the FUSE vnode lookup operation and namei-specific create/delete/rename lookup handling.

Key behavior:
- Checks execute access on the directory and rejects delete/rename on read-only mounts.
- Handles `.` and `..` in-kernel; parent inode numbers are cached on directory nodes for later dotdot lookup.
- Sends `FBT_LOOKUP` to userspace for normal names, with NUL-terminated component payloads.
- For create/rename last-component misses, verifies write access, sets `SAVENAME`, optionally unlocks parent, and returns `EJUSTRETURN`.
- Handles `DELETE` and `RENAME` final-component cases by checking directory write permission and returning parent/target state expected by VFS.
- Uses `VFS_VGET()` to materialize looked-up inode numbers and assigns returned vnode type from daemon attributes.
- On selected failures, sends `FBT_RECLAIM` for non-root, non-self inodes that need daemon cleanup.

Filesystem relevance:
- This is the main bridge between OpenBSD `namei()` semantics and FUSE daemon lookup responses.
- Correct parent locking and `PDIRUNLOCK`/`SAVENAME` behavior are essential for subsequent create/remove/rename vnode ops.
