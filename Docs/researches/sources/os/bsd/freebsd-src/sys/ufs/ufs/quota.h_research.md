# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/quota.h

## Purpose
Defines UFS quota constants, on-disk quota formats, quotactl commands, kernel `dquot` structure, quota locking helpers, and quota function declarations.

## Key Contents
- Grace period defaults:
  - `MAX_IQ_TIME`
  - `MAX_DQ_TIME`
- Quota types:
  - `MAXQUOTAS`
  - `USRQUOTA`
  - `GRPQUOTA`
- Default quota file names:
  - `INITQFNAMES`
  - `QUOTAFILENAME`
  - `QUOTAGROUP`
- `quotactl` command composition:
  - `SUBCMDMASK`, `SUBCMDSHIFT`, `QCMD`
  - `Q_QUOTAON`, `Q_QUOTAOFF`
  - 32-bit commands: `Q_GETQUOTA32`, `Q_SETQUOTA32`, `Q_SETUSE32`
  - 64-bit commands: `Q_GETQUOTA`, `Q_SETQUOTA`, `Q_SETUSE`
  - `Q_SYNC`, `Q_GETQUOTASIZE`
- On-disk quota records:
  - `struct dqblk32`
  - `struct dqblk64`
  - `dqblk` alias to `dqblk64`
- 64-bit quota file header:
  - `Q_DQHDR64_MAGIC`
  - `Q_DQHDR64_VERSION`
  - `struct dqhdr64`
- Kernel `struct dquot`:
  - Hash/free-list linkage.
  - Mutex, flags, type, refcount, id, owning `ufsmount`.
  - Embedded `struct dqblk64`.
- Dquot flags:
  - `DQ_LOCK`, `DQ_WANT`, `DQ_MOD`, `DQ_FAKE`, `DQ_BLKS`, `DQ_INODS`
- Field aliases:
  - `dq_bhardlimit`, `dq_bsoftlimit`, `dq_curblocks`, etc.
- Helpers:
  - `NODQUOT`
  - `FORCE`, `CHOWN`
  - `DQREF`
  - `DQI_LOCK`, `DQI_UNLOCK`, `DQI_WAIT`, `DQI_WAKEUP`
- Kernel declarations:
  - Accounting: `chkdq`, `chkiq`, `getinoquota`
  - Lifecycle: `dqinit`, `dquninit`, `dqrele`
  - Sync/control: `qsync`, `qsyncvp`, `quotaon`, `quotaoff`, `ufs_quotactl`
  - Quota get/set variants.
  - Soft updates quota hooks under `SOFTUPDATES`.
- Userland declaration:
  - `quotactl(const char *, int, int, void *)`

## Interactions
- Included by `inode.h` and UFS implementation files because `struct inode` contains dquot pointers.
- Used by allocation, truncation, write, and ownership-change paths to enforce quota limits.
