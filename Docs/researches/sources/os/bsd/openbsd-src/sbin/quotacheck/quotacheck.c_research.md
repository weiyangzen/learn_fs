# File Research: sources/os/bsd/openbsd-src/sbin/quotacheck/quotacheck.c

## Purpose

Checks and repairs UFS/FFS quota usage files by scanning raw filesystem inodes and reconciling observed block/inode usage with user and group quota files and active kernel quota state.

## Main Flow

`main()` requires root via `checkroot()`, parses preen/debug/group/user/verbose/maxparallel flags, preloads known group and user ids into hash tables, then either delegates to `checkfstab()` in preen mode or walks `/etc/fstab` manually. It selects read-write `ffs`, `ufs`, and `mfs` filesystems with quota options through `needchk()`, matches explicit arguments by mount realpath or device identity, normalizes devices with `blockcheck()`, and calls `chkquota()`.

## Filesystem Scan

`chkquota()` forks so each filesystem check can run independently or under preen scheduling. The child opens the raw device read-only, syncs, searches known superblock locations, validates UFS1/UFS2 magic and size, computes `maxino`, then scans every cylinder group. It reads cylinder group blocks, determines initialized inode count, streams inode blocks through `getnextinode()`, skips invalid/free/root-below inodes, and accumulates inode and block counts per gid/uid for regular files, directories, and symlinks.

The inode access layer uses an optimized sequential buffer sized around `INOBUFSIZE`, rounded to filesystem block size. `setinodebuf()` prepares per-cylinder-group counters, `getnextinode()` reads the next chunk with `bread()`, and `freeinodebuf()` releases the buffer.

## Quota File Reconciliation

`update()` opens or creates the quota file, sets owner/group/mode on creation, opens a read stream too, tries `quotactl(Q_SYNC)`, then iterates from id zero through the highest known id. For each `dqblk`, it compares stored current inodes/blocks to scanned usage. Differences are printed in debug/verbose mode, grace timers are reset when crossing soft limits from below to above, current usage fields are updated, and non-debug mode writes the quota file and calls `quotactl(Q_SETUSE)`. Finally it truncates the quota file to the highest id plus one record.

## Helpers And Data Structures

Usage data is stored in `struct fileusage` hash tables split by quota type. `hasquota()` parses fstab mount options for `userquota`/`groupquota` names and optional paths. `oneof_realpath()` and `oneof_specname()` match CLI filesystem arguments to fstab entries. `addid()` creates missing usage records and tracks `highid[type]`; unnamed ids are formatted numerically.

## Risks And Invariants

- Only UFS1/UFS2-like filesystems with valid superblocks are processed.
- `done` uses a 64-bit bitset and the source comment notes it supports at most 64 explicit filesystem arguments.
- Quota file iteration runs through `highid`, so unexpectedly large uid/gid values can make update work proportional to the numeric id range.
- The inode soft-limit reset code compares `dqb_curblocks` in both block and inode branches; that mirrors the source and is a behavior to verify before changing.
- In debug mode quota files are read and compared but not written/truncated.
