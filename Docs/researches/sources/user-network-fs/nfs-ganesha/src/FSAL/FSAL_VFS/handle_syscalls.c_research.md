# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/handle_syscalls.c

Purpose: this shared file implements OS-independent helper logic around symlink reads and root handle acquisition for VFS filesystems.

Important functions: `vfs_readlink` refreshes cached symlink content by opening/statting a symlink handle, allocating `st_size + 1`, calling `vfs_readlink_by_handle`, NUL-terminating, and updating the VFS object. It has FreeBSD-specific `fhstat` behavior. `vfs_get_root_handle` opens the filesystem path as a directory, optionally changes fsid indexing to the configured type, logs the resulting fsid, and calls OS `vfs_re_index`.

Control flow and state: `vfs_readlink` frees old link content before refresh and restores the object to NULL/zero length on error. `vfs_get_root_handle` returns an opened root fd via output parameter; the caller stores it in filesystem private data and later closes it during unclaim.

Dependencies and integration points: uses `vfs_fsal_open`, `vfs_stat_by_handle`, `vfs_readlink_by_handle`, `change_fsid_type`, and OS-specific `vfs_re_index`. Called from `handle.c` readlink paths and `export.c` filesystem claiming.

Risks: symlink size can change between stat and readlink, yielding truncation or errors. Root fd acquisition must happen before Linux `open_by_handle_at` can work. Reindex failure closes the root fd and prevents filesystem claiming.

Test signals: symlink refresh on changed targets, ENOENT-to-stale behavior, allocation cleanup on readlink failures, fsid_type override, and platform-specific reindex behavior.
