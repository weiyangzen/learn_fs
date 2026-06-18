## sources/user-network-fs/samba/source3/lib/sysquotas_4A.c

Purpose: quota backend for systems with the 4-argument `quotactl(int cmd, char *special, qid_t id, caddr_t addr)` style, historically HPUX/IRIX-like platforms.

Important APIs are `sys_get_vfs_quota` and `sys_set_vfs_quota`, compiled only under `HAVE_SYS_QUOTAS` and `HAVE_QUOTACTL_4A`. Compatibility macros normalize quota command names, group quota support, quota block size, and alternate `dqblk` field names.

Control flow: get switches on Samba quota type. User/group quota reads call `quotactl(QCMD(Q_GETQUOTA,...), bdev, id, &D)` and tolerate `EDQUOT`; filesystem quota types query the current UID/GID and set `QUOTAS_DENY_DISK` when the query succeeds. Results are copied from `struct dqblk` into `SMB_DISK_QUOTA` with `QUOTABLOCK_SIZE`. Set translates Samba limits into native block units, calls `Q_SETQLIM` for user/group IDs, and for filesystem quota enable/disable only verifies whether the current enforcement flags already match because real toggling is documented as unreliable.

State and persistence: quota changes persist through the OS quota subsystem. No local state is stored. Dependencies are platform quota headers and Samba quota types.

Risks: group quota paths only exist under `HAVE_GROUP_QUOTA`, so unsupported group requests fall through to `ENOSYS`. Filesystem quota toggling is not implemented, only compared. Block-size conversion can truncate. The file compiles a dummy symbol when unsupported. Tests are platform/build-matrix tests that mock or exercise 4A `quotactl`, block conversion, EDQUOT handling, and unsupported quota types.
