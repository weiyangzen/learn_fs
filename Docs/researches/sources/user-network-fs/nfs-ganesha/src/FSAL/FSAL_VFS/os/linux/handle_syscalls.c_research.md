# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/linux/handle_syscalls.c

Purpose: this file implements Linux-specific persistent VFS handle encoding, validation, extraction, and reopening using `name_to_handle_at` and `open_by_handle_at`.

Important functions and format: the first handle byte stores fsid type, handle type width flags, and a dummy flag. `display_vfs_handle` decodes the fsid, type, dummy marker, and opaque bytes for logging. `vfs_map_name_to_handle_at` calls `name_to_handle_at`, encodes the configured fsid, encodes the kernel handle type as 8/16/32 bits, appends opaque kernel handle bytes, and enforces `VFS_HANDLE_LEN`. `vfs_open_by_handle` reconstructs `struct file_handle` from the encoded bytes and calls `open_by_handle_at(root_fd(fs), ...)`. `vfs_fd_to_handle`, `vfs_name_to_handle`, `vfs_extract_fsid`, `vfs_encode_dummy_handle`, `vfs_is_dummy_handle`, `vfs_valid_handle`, and `vfs_re_index` complete the interface.

Control flow and state: Linux handles require a live root fd for the mount stored during filesystem claim. Fsid is embedded in the NFS-visible handle so incoming handles can be mapped back to the correct `fsal_filesystem`. Dummy handles encode only fsid and cannot be reopened.

Dependencies and integration points: uses Linux file handle syscalls, FSAL fsid encode/decode helpers, and the VFS root fd stored by `export.c`. Common handle and export code call these functions through `fsal_handle_syscalls.h`.

Risks: handle size limits are tight; Btrfs/GPFS-like 40-byte handles plus wide fsids and 32-bit handle types can exceed the NFS handle budget. Validation must account for fsid length, type width, minimum and maximum kernel handle sizes. `open_by_handle_at` maps `ENOENT` to `ESTALE`; permission/capability failures can surface as FSAL errors. Dummy handles must not be treated as reopenable.

Test signals: ext4/xfs/btrfs-style handle sizes, all fsid types, 8/16/32-bit handle types, invalid first byte/type flags, oversized handles, deleted-file stale opens, dummy handles, and root fd closure/reopen failures.
