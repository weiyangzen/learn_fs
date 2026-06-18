# File Research: sources/os/linux/linux-stable/fs/quota/quota.c

## Purpose
Implements the syscall-facing quota control layer for `quotactl(2)` and `quotactl_fd(2)`. It validates permissions, resolves target superblocks, translates user ABI structures to internal quota control structures, and dispatches to filesystem quota operations.

## Main Responsibilities
- Permission enforcement in `check_quotactl_permission()`, allowing unprivileged reads of owned user/group quotas but requiring `CAP_SYS_ADMIN` for most operations.
- Global quota sync for `Q_SYNC` without a specific device.
- Dispatch of classic VFS quota commands and XFS-compatible quota commands.
- Conversion between:
  - `if_dqblk` and `qc_dqblk`,
  - `if_dqinfo` and `qc_info`,
  - `fs_disk_quota` and `qc_dqblk`,
  - `fs_quota_stat` / `fs_quota_statv` and `qc_state`.
- Compat ABI handling for alignment-sensitive structures and compat syscalls.
- Superblock lookup by block device for `quotactl`.
- File-descriptor-based superblock targeting for `quotactl_fd`.

## Key Dispatch Paths
- `do_quotactl()` validates quota type support and calls specific helpers for `Q_QUOTAON`, `Q_QUOTAOFF`, `Q_GETQUOTA`, `Q_SETQUOTA`, `Q_XGETQSTAT`, `Q_XSETQLIM`, etc.
- `quotactl_block()` looks up the mounted superblock for a block device and handles freeze/thaw waiting and exclusive locking for quota on/off commands.
- `quotactl_fd()` uses an already open file's mount superblock and write access guards for mutating commands.

## Edge Cases
- `Q_XQUOTASYNC` is treated as a no-op for coherent XFS-style quotas after read-only checks.
- Project quota state is squeezed into older XFS stat ABI fields only when group quota data is absent.
- Bigtime quota timer support maps high timer bits via `FS_DQ_BIGTIME`.
- `array_index_nospec()` is used before indexing quota type arrays.
