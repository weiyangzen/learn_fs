## sources/user-network-fs/samba/source3/lib/sysquotas_jfs2.c

Purpose: AIX JFS2 quota backend. It exists because JFS2 uses different quota commands from the generic 4B backend and requires root even for some documented read cases.

Important APIs are `sys_get_jfs2_quota` and `sys_set_jfs2_quota`, plus private `sys_quotactl_JFS2`. Compilation is guarded by `HAVE_JFS_QUOTA_H` and `Q_J2GETQUOTA`.

Control flow: `sys_get_jfs2_quota` selects user/group or current effective user/group based on `enum SMB_QUOTA_TYPE`, calls `sys_quotactl_JFS2` with `Q_J2GETQUOTA`, and copies `quota64_t` fields into `SMB_DISK_QUOTA` using `QUOTABLOCK_SIZE` and `QUOTAS_ENABLED | QUOTAS_DENY_DISK`. `sys_quotactl_JFS2` always becomes root around `quotactl`, logs unsupported/unconfigured errors selectively, and returns the native result. Setting quota is intentionally unsupported and returns `ENOSYS` because JFS2 limit classes do not map cleanly to Samba’s model.

State and persistence: read-only from Samba’s perspective; setting is not persisted because it is refused. Dependencies are AIX JFS quota headers, Samba privilege helpers, and quota types.

Risks: unconditional root elevation around reads must be audited for balanced `unbecome_root` under all paths; this file does restore after the call. Lack of set support means administrator UI paths must handle `ENOSYS`. Tests should cover all get quota types on AIX/JFS2, unsupported type behavior, and set returning `ENOSYS`.
