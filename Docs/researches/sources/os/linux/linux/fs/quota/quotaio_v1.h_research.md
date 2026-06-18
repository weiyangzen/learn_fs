# File Research: sources/os/linux/linux/fs/quota/quotaio_v1.h

On-disk structure definitions for the old v1 quota format.

Defines:
- Default soft-limit grace times:
  - `MAX_IQ_TIME`: one week for inode quota.
  - `MAX_DQ_TIME`: one week for block quota.
- `struct v1_disk_dqblk`, the flat-array quota record:
  - block hard/soft limits,
  - current block count,
  - inode hard/soft limits,
  - current inode count,
  - block and inode grace timers.
- `v1_dqoff(UID)`, the byte offset of a quota record in the flat file.

Research notes:
- Timer fields use `unsigned long`, explicitly noted as architecture-width dependent.
- The file is included by `quota_v1.c`.
