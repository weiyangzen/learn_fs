# File Research: sources/os/bsd/freebsd-src/sbin/fsck/preen.c

This file implements `checkfstab()`, the generic `/etc/fstab` traversal and preen-mode scheduling helper used by filesystem checkers. It is not UFS-specific; it receives callbacks that decide whether an fstab entry should be checked and how to launch the concrete checker.

Key behavior:
- Iterates fstab entries by increasing `fs_passno`, using `setfsent()` / `getfsent()`.
- In non-preen mode, pass 1, or background mode, checks filesystems serially through `checkit`.
- In preen mode for later passes, groups partitions by disk and runs checks for different disks in parallel while serializing partitions on the same disk.
- Tracks failed partitions in `badh` and prints the final “unexpected inconsistency” summary.
- Honors the fstab `failok` option by ignoring a checker error for that filesystem.
- Uses `finddisk()` to derive a disk base name by trimming after the unit-number portion, then queues partitions under that disk.

Important interactions:
- `docheck(struct fstab *)` filters entries.
- `checkit(type, dev, mountpoint, auxarg, pidp)` either runs synchronously or starts a child and returns its pid through `pidp`.
- Uses `wait()` to collect parallel checker children and starts the next partition on a disk after the previous one finishes.

Edge cases:
- Duplicate fstab devices are warned and skipped per disk queue.
- Unknown child pids are ignored with a warning.
- Signal exits force an error return.
- `name == NULL` is fatal in preen paths but skipped in manual mode.
