## sources/user-network-fs/samba/source3/lib/sysquotas_xfs.c

Purpose: XFS/GFS/GFS2 quota backend using XFS quota-manager commands and `fs_disk_quota`/`fs_quota_stat`. It supports user/group quota records and enforcement/accounting state for filesystem quota types.

Important APIs are `sys_get_xfs_quota` and `sys_set_xfs_quota`. Compatibility macros normalize XFS command names on IRIX-like systems, and `BBSIZE` defines the native block unit.

Control flow: get switches by quota type. User/group record reads call `Q_XGETQUOTA`; `ENOENT` is normalized to success with zero quota because XFS reports missing quota records that way. Filesystem quota reads call `Q_XGETQSTAT` and inspect `XFS_QUOTA_UDQ_*` or `XFS_QUOTA_GDQ_*` flags to set `QUOTAS_DENY_DISK` or `QUOTAS_ENABLED`. Set converts block limits to basic blocks, sets `FS_DQ_LIMIT_MASK`, and uses `Q_XSETQLIM` for user/group. For filesystem quota types it queries status, turns enforcement/accounting on or off using `Q_XQUOTAON`/`Q_XQUOTAOFF` according to requested flags, and returns failure if neither enabled nor deny-disk is requested.

State and persistence: all state is kernel/filesystem quota state. No local storage. Dependencies include XFS quota headers, Linux/IRIX quota macros, Samba quota types, and privilege inherited from caller.

Risks: quota-on/off sequencing can partially succeed if one call succeeds and a later call fails. Return values for intermediate status queries are not always checked. Group quota support is forced by macro in this file. Tests should cover `ENOENT` normalization, fs state flag mapping, q_on/q_off transitions, block conversion, and invalid `qflags`.
