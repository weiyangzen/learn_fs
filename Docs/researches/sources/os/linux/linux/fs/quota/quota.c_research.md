# File Research: sources/os/linux/linux/fs/quota/quota.c

System-call and ABI translation layer for quota control. It handles `quotactl(2)` and `quotactl_fd(2)`, translates legacy/Linux/XFS quota structures into VFS `qc_*` structures, checks permissions, locates target superblocks, and dispatches to `sb->s_qcop`.

Key responsibilities:
- `check_quotactl_permission()` enforces command permissions and LSM `security_quotactl()`.
- `quota_sync_all()` implements device-less `Q_SYNC` across all superblocks.
- `quota_quotaon()` / `quota_quotaoff()` route to either traditional quota file operations or sysfile enforcement toggles.
- Legacy quota ABI:
  - `quota_getfmt()`
  - `quota_getinfo()` / `quota_setinfo()`
  - `quota_getquota()` / `quota_getnextquota()`
  - `quota_setquota()`
- XFS-style ABI:
  - `quota_getxstate()` / `quota_getxstatev()`
  - `quota_setxquota()`
  - `quota_getxquota()` / `quota_getnextxquota()`
  - `quota_rmxquota()`
- `do_quotactl()` validates quota type and dispatches all quota commands.
- `quotactl_block()` resolves a block-device path to a mounted superblock and handles freeze/exclusive locking semantics.
- `SYSCALL_DEFINE4(quotactl)` implements path/block-device based quota control.
- `SYSCALL_DEFINE4(quotactl_fd)` implements fd-based quota control.

Important conversions:
- Converts block units between legacy `QIF_DQBLKSIZE` and byte-based `qc_dqblk`.
- Converts XFS basic blocks using local `quota_bbtob()` / `quota_btobb()`.
- Supports `FS_DQ_BIGTIME` high timer fields when translating XFS-style quota timers.
- Handles compat alignment fixups for older quota structs.

Important behavior:
- `Q_GETQUOTA` and `Q_GETNEXTQUOTA` are treated as write-like commands because reading can instantiate dquots or update on-disk references in some filesystems.
- Quota-on/off commands acquire `s_umount` for write; other commands acquire it for read.
- `Q_QUOTAON` resolves the quota file path before grabbing `s_umount` to avoid autofs/pathwalk deadlocks.
- `quotactl_fd()` uses mount write access for write-like commands.

Research notes:
- This file intentionally remains present even when full VFS quota support is disabled, because syscall plumbing and command validation still need definitions.
- Actual generic quota state is implemented in `dquot.c`; this file is mostly ABI adaptation and dispatch.
