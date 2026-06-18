## sources/user-network-fs/samba/source3/lib/sysquotas_linux.c

Purpose: Linux default quota backend using Linux `quotactl` and `struct dqblk` semantics. It is compiled for `HAVE_SYS_QUOTAS` plus `HAVE_QUOTACTL_LINUX`.

Important APIs are `sys_get_vfs_quota` and `sys_set_vfs_quota`. They translate between Linux quota fields and Samba `SMB_DISK_QUOTA`, including block size normalization and inode limits.

Control flow: get validates pointers, zeroes output, switches on quota type, calls `quotactl(Q_GETQUOTA)` for supplied UID/GID or effective UID/GID, and for filesystem quota types treats successful current-user/current-group reads as evidence for `QUOTAS_DENY_DISK`. It stores `curblocks` as `dqb_curspace / QUOTABLOCK_SIZE`. Set fills `dqb_bsoftlimit`, `dqb_bhardlimit`, inode limits, and `dqb_valid = QIF_LIMITS` for user/group writes. For filesystem quota types it does not toggle enforcement; it compares current query success with requested `QUOTAS_DENY_DISK` and succeeds only if already matching, else returns `EPERM`.

State and persistence: quota records are persisted by the Linux kernel/filesystem. No local state. Dependencies are `<sys/quota.h>`, Samba quota types, debug logging, and platform macros.

Risks: quota enforcement toggling is deliberately not implemented for fs quota types. `curspace / bsize` truncates partial blocks. Pointer validation panics instead of returning errors. Tests should cover user/group get/set, filesystem type comparison behavior, block-size conversions, `QIF_LIMITS`, and unsupported type `ENOSYS`.
