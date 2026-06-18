# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/export.c

This file implements SaunaFS export operations: export release, path lookup, dynamic filesystem information, state allocation/freeing, wire/host handle conversion, handle reconstruction, supported attributes/ACL reporting, and operation-vector initialization.

Key functions are `release`, `lookup_path`, `get_dynamic_info`, `fs_free_state`, `allocate_state`, `wire_to_host`, `host_to_key`, `create_handle`, `fs_acl_support`, `fs_supported_attrs`, `get_fsal_obj_hdl`, and `exportOperationsInit`. `allocate_state` creates a `SaunaFSStateFd` with an embedded `SaunaFSFd` initialized as `FSAL_FD_STATE`. `wire_to_host` validates and endian-converts a `sau_inode_t`; `host_to_key` adds the current export id into `SaunaFSHandleKey`; `create_handle` rehydrates an inode handle by calling `saunafs_getattr`.

Control flow for root/path lookup validates exported path prefixes, special-cases `/`, then calls `saunafs_lookup` below `SPECIAL_INODE_ROOT` and allocates a handle. Release tears down root handle, detaches export ops, drains the fileinfo cache by forcing zero timeout/size, releases cached SaunaFS file handles, destroys the client instance, frees duplicated `subfolder`, and frees the export.

State and persistence are per-export: `sau_t *fsInstance`, root handle, cached DS fileinfo entries, and FSAL open states. Persistent metadata remains in SaunaFS. Dynamic stats come from `sau_statfs`.

Dependencies include Ganesha common FSAL/export helpers, `context_wrap`, private types, ACL option checks, and SaunaFS statfs/getattr APIs. Integration points are `main.c` export creation and all handle reconstruction after NFS filehandle cache misses.

Risks include path-prefix validation edge cases, cleanup ordering with pNFS DS references, forced cache draining while handles may be in use, and endian assumptions for 32-bit `sau_inode_t`. Test signals should cover root lookup, non-root path lookup, stale wire handle reconstruction, big-endian/little-endian handle conversion, ACL-disabled exports, statfs mapping, and export release with populated DS cache.
