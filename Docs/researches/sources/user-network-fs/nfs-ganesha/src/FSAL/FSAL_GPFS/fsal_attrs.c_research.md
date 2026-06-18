# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_attrs.c

Purpose: this file implements GPFS FSAL attribute retrieval and mutation. It retrieves fs_locations, xstat/ACL data, filesystem statistics by file handle, and applies setattr operations including size, reserved space, mode, owner, group, timestamps, and NFSv4 ACLs.

Important APIs and functions: `GPFSFSAL_fs_loc()` calls `OPENHANDLE_FS_LOCATIONS`, builds `nfs4_fs_locations`, and stores root/path/server data in the attrlist. `GPFSFSAL_getattrs()` calls `fsal_get_xstat_by_handle()` with optional ACL buffers, retries with heap buffers if the embedded ACL buffer is too small, fills fallback FSID for older GPFS, and calls `gpfsfsal_xstat_2_fsal_attributes()`. `GPFSFSAL_statfs()` calls `OPENHANDLE_STATFS_BY_FH`. `GPFSFSAL_setattrs()` converts FSAL attr masks into GPFS xstat masks and optional NFSv4 ACL buffers, then calls `fsal_set_xstat_by_handle()`.

Control flow: getattr initializes FSID defaults, determines whether expiration and ACLs were requested, tries the stack ACL buffer first, grows to `acl_buf->acl_len` on retry, and converts only after a successful xstat fetch. Setattr first validates time-setting support, applies export umask to mode, fills `buffxstat` and mask bits for requested attrs, converts ACLs when enabled and present, then sends a single xstat update if anything changed.

State and persistence: attributes are persisted through GPFS openhandle xstat calls. The file manages temporary ACL buffers and `attrs->fs_locations` lifetime by releasing old data before replacing it. `expire_time_attr` can update attribute cache expiration in `fsal_attrlist`.

Dependencies and integration: depends on `gpfs_ganesha`, GPFS xstat structures, `fsal_acl_2_gpfs_acl()` from `fsal_convert.c`, GPFS filesystem private data, export ACL policy, and common FSAL attr/mask helpers.

Risks and test signals: ACL retry logic assumes `acl_buf->acl_len` is valid after a too-small response. Symlink chmod is intentionally ignored. `ignore_mode_change` can suppress mode changes per export. `ATTR4_SPACE_RESERVED` reuses `st_size` in the GPFS stat buffer and must match lower-layer expectations. Tests should cover ACL disabled/enabled getattrs, oversized ACL retry, RDATTR_ERR behavior, fs_locations allocation/release, statfs `EUNATCH`, setattr time support rejection, umask mode changes, symlink mode ignores, ACL inheritance validation through convert, and heap ACL cleanup on errors.
