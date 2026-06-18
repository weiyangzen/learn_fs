# File Research: sources/os/bsd/freebsd-src/sbin/quotacheck/preen.c

`quotacheck -a` preen scheduler that processes fstab entries by pass number and disk.

Key elements:
- Defines `partentry` for a filesystem/quota pair and `diskentry` for a disk base name with a partition queue and child pid.
- `checkfstab` walks `/etc/fstab` by pass number, opens user/group quota files as requested, checks pass-1 filesystems directly, queues later passes by disk, forks one child per disk, waits, records failures, and starts the next partition on a disk when the previous child exits.
- `finddisk` groups device names by base disk name, stopping after the first numeric unit sequence.
- `addpart` converts the fstab spec through `blockcheck`, stores mountpoint/quota handles, and rejects duplicate device entries within a disk queue.
- `startdisk` forks and runs `chkquota` for the first queued partition.

Dependencies:
- Uses `quotacheck.h`, libutil quota APIs, fstab APIs, `TAILQ`, and `emalloc`/`estrdup` helpers supplied by linked fsck utilities.

Research notes:
- Failed partitions are retained in `badh` for a final “unexpected inconsistency” summary.
- Successful child completion closes quota files in the parent; failed entries remain allocated until process exit for summary reporting.
