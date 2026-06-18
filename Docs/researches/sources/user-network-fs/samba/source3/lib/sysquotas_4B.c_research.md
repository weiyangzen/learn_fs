## sources/user-network-fs/samba/source3/lib/sysquotas_4B.c

Purpose: quota backend for BSD-derived `quotactl(const char *path, int cmd, int id, char *addr)` systems, with Darwin-specific privilege workaround support.

Important functions are private translators `xlate_qblk_to_smb`, `xlate_smb_to_qblk`, syscall wrapper `sys_quotactl_4B`, and exported `sys_get_vfs_quota`/`sys_set_vfs_quota`. It maps native `struct dqblk` fields to `SMB_DISK_QUOTA` and sets `QUOTAS_ENABLED | QUOTAS_DENY_DISK` on successful reads.

Control flow: `sys_get_vfs_quota` selects user, current-user filesystem, group, or current-group filesystem quota by choosing USRQUOTA/GRPQUOTA and supplied or effective IDs. `sys_quotactl_4B` logs the operation, optionally becomes root for Darwin HFS, calls `quotactl`, suppresses noisy logs for common unsupported/unconfigured quota errors, and restores privileges. Set converts limits and calls `Q_SETQUOTA` for the requested ID/type.

State and persistence: native quota state is persisted by the filesystem. There is no local state. Dependencies include BSD quota headers, optional UFS/JFS headers, Samba privilege helpers, and quota structs.

Risks: filesystem quota types are treated as quota records for the current effective UID/GID rather than quota-enforcement toggles, unlike XFS. Debug detection of get/set via bit tests on `cmd` is approximate. The Darwin root workaround increases privilege-sensitive surface. Tests should cover translation with byte-vs-block native fields, Darwin root enter/leave, ENOTSUP/EINVAL handling, and all four Samba quota types.
