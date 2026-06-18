# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_quota1.h

Read completely: 105 lines.

Defines the legacy quota1 on-disk format and compatibility command constants.

Key constants:
- `MAX_IQ_TIME` and `MAX_DQ_TIME` define one-week default grace periods for inode and block soft-limit violations.
- `QUOTAFILENAME` and `QUOTAGROUP` provide historical quota file/group names.
- `QCMD()`, `SUBCMDMASK`, `SUBCMDSHIFT`, and `Q_QUOTAON` through `Q_SYNC` define old `compat_50_quotactl` command encoding.

On-disk format:
- `struct dqblk` is the quota1 file record indexed by id.
- Stores 32-bit block hard/soft limits, current block usage, inode hard/soft limits, current inode usage, and 32-bit block/inode grace expiration times.

Conversion prototypes:
- `lfs_dqblk_to_quotavals()` converts a legacy record into filesystem-independent block/file `quotaval` structures.
- `lfs_quotavals_to_dqblk()` performs the reverse conversion.

Risks and notes:
- The header explicitly marks quota1 as deprecated in favor of quota2.
- The quota1 file format is limited to 32-bit limits/usages and uses zero to represent no limit.
