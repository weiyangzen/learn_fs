# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/subfsal_helpers.c

Purpose: this helper implements referral filesystem-location extraction for VFS sub-FSALs using a `user.fs_location` xattr.

Important function: `vfs_get_fs_locations` opens the directory if no fd is supplied, resolves `/proc/self/fd/<fd>` to a real path, rewrites the path from export full path to pseudopath when needed, reads `user.fs_location` through VFS xattr helpers, parses it as `server:path`, and creates an `nfs4_fs_locations` structure with one server.

Control flow and state: the function may replace `attrs_out->fs_locations`, set `ATTR4_FS_LOCATIONS`, and close only fds it opened locally. It releases any existing fs_locations before populating a new one.

Dependencies and integration points: used by `vfs/vfs/attrs.c` common attr hook and `handle.c` referral population. Depends on `/proc/self/fd`, export context macros, `vfs_getextattr_value`, and NFSv4 fs_locations helpers.

Risks: Linux `/proc/self/fd` availability is assumed. Path rewrite checks total length but depends on the fd path starting with `CTX_FULLPATH(op_ctx)`. The xattr parser requires a colon; malformed values clear locations without returning a hard error. Single-server support may be too narrow for complex referrals.

Test signals: referrals with full path equal/different from pseudopath, missing xattr, malformed xattr, long pseudopath rewrite, supplied fd versus local open, and cleanup of previous fs_locations.
