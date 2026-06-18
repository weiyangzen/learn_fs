# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/main.c

This file is the `fsck_ffs` entry point and top-level orchestration layer.

Key behavior:
- Parses flags for alternate superblock, background check, conversion, debug, erase/zero free blocks, force, background feasibility check, lost+found mode, assume no/yes, preen, restart, inode trimming, surrender on reads, and directory-space zeroing.
- Sets signal handlers for interruption, `SIGINFO`, and background progress alarms.
- Raises data-size rlimit to support large filesystems.
- `checkfilesys()` performs one filesystem check from device resolution through final status.
- Handles mounted-filesystem lookup, block-device canonicalization, superblock open/read, and `-F` background feasibility exits.
- Runs fast gjournal cleanup when possible.
- Sets up background snapshot checking through `setup_bkgrdchk()`.
- Runs SUJ recovery when enabled and safe; falls back to full fsck if journal recovery fails or is disallowed.
- Offers to add supported metadata check hashes in manual writable UFS2 mode.
- Executes phases: pass1, optional pass1b, pass2, pass3, pass4, snapflush, pass5.
- Prints final allocation/free summary and duplicate residuals in debug mode.
- Marks clean/dirty through `ckfini()`, requests rerun/restart when needed, and asks mount reload logic via `chkdoreload()`.

Background setup:
- Requires mounted read-write soft-updates filesystem with kernel support.
- Creates `.snap` if necessary, creates `.snap/fsck_snapshot` via `nmount(..., snapshot)`, opens it, unlinks it immediately, rereads the snapshot superblock, and stores the fd handle for sysctl commands.
- Verifies sysctl support for reference count, block count, size, free file/dir/block operations, and optionally summary adjustments.

Important interactions:
- Calls `setup()`, `pass1()` through `pass5()`, `suj_check()`, `gjournal_check()`, and many utility routines.
- Uses exit/status values including `EEXIT`, `ERERUN`, and `ERESTART`.
