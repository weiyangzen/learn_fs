# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/export.c

Purpose: Implements LizardFS FSAL export operations: export release, path lookup, wire-handle conversion, handle reconstruction, dynamic filesystem info, static capability accessors, state allocation, and fd-to-object lookup.

Important APIs and types: Core methods are `lzfs_fsal_release`, `lzfs_fsal_lookup_path`, `lzfs_fsal_wire_to_host`, `lzfs_fsal_create_handle`, `lzfs_fsal_get_fs_dynamic_info`, `lzfs_fsal_fs_supports`, `lzfs_fsal_alloc_state`, `lzfs_free_state`, `get_fsal_obj_hdl`, and `lzfs_fsal_export_ops_init()`. State allocation uses `struct lzfs_fsal_state_fd`.

Control flow: `lzfs_fsal_release()` deletes the root handle, detaches the export, drains and destroys the pNFS fileinfo cache, destroys the LizardFS client instance, frees the configured subfolder, and frees the export. `lookup_path()` validates and strips the Ganesha export full path, special-cases root, then uses `liz_cred_lookup()` from `SPECIAL_INODE_ROOT` to fetch attributes and allocate a handle. Wire conversion swaps a `liz_inode_t` in place based on endianness flags. Handle reconstruction validates inode descriptor size, gets attrs by inode, and allocates a handle.

State and persistence: Export state owns the mounted `liz_t` instance, root handle, pNFS fileinfo cache, LizardFS init parameters, and pNFS feature flags. Per-open NFS state owns an `lzfs_fsal_fd` initialized with `FSAL_FD_STATE`.

Dependencies and integration: Uses Ganesha FSAL config/commonlib, `fsal_convert`, `context_wrap`, `lzfs_internal`, and LizardFS statfs/getattr APIs. `lzfs_fsal_export_ops_init()` is called during export creation in `main.c`.

Risks: `lookup_path()` returns the shared root handle for root without taking an obvious extra reference in this function; correctness depends on Ganesha calling conventions. Path prefix validation uses `strstr(real_path, CTX_FULLPATH(op_ctx)) == real_path`, which can be sensitive to normalized slashes and path aliases. `wire_to_host()` mutates the caller buffer before length validation. Cleanup must avoid releasing cached fileinfo after the LizardFS instance is destroyed; current ordering is correct but high risk.

Test signals: Export mount/unmount under normal and pNFS DS modes, root and non-root lookup paths, big-endian wire handles, stale inode reconstruction, statfs values, state allocation/free under NFSv4 opens, and config reload/release leak checks.
