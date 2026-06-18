# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/handle_syscalls.c

## Purpose

This file implements the FSAL_VFS handle syscall layer for XFS using libhandle and XFS ioctls. It converts between file descriptors, names, XFS file handles, FSAL FSIDs, dummy export handles, and root mount handles. The source was read as a complete 416-line file.

## Important APIs, Types, and Functions

Important functions are `display_xfs_handle`, `xfs_fsal_bulkstat_inode`, `xfs_fsal_inode2handle`, `vfs_open_by_handle`, `vfs_fd_to_handle`, `vfs_name_to_handle`, `vfs_readlink`, `vfs_extract_fsid`, `vfs_encode_dummy_handle`, `vfs_is_dummy_handle`, `vfs_valid_handle`, and `vfs_get_root_handle`. It uses `xfs_handle_t`, `xfs_bstat`, `XFS_IOC_FSBULKSTAT_SINGLE`, `fd_to_handle`, `open_by_handle`, `readlink_by_handle`, `path_to_fshandle`, and FSAL `encode_fsid`/`decode_fsid`.

## Control Flow

Regular files and directories get handles from an opened fd through libhandle. Other object types use `fstatat` and XFS bulkstat to synthesize handle contents from inode/generation while copying FSID from a reference fd. Open-by-handle maps `ENOENT` to stale. Root setup opens the mount point, obtains the root handle, extracts its FSID, and re-indexes the FSAL filesystem by that XFS FSID.

## State and Persistence Behavior

No persistent state is written. File-handle bytes encode XFS FSID, inode, generation, and a dummy marker in `fid_pad` for synthetic FSID-only handles. `vfs_get_root_handle` temporarily opens the root directory and updates in-memory FSAL filesystem indexing.

## Dependencies and Integration Points

This is XFS-specific glue for prototypes in `vfs_methods.h`. It depends on libhandle headers/runtime and FSAL localfs indexing. It is called by generic VFS export/handle code.

## Risks and Edge Cases

Handle size checks use caller-provided `handle_len`; undersized buffers fail with `E2BIG`. Dummy handles overload `fid_pad`, so validation must reject unsupported FSID types and nonzero generations. `vfs_get_root_handle` closes and resets `root_fd`, so callers should not expect it to keep an fd open.

## Test Signals

Run on real XFS with libhandle support: fd/name/open-by-handle round trips, symlink `readlink_by_handle`, socket/device lookup via bulkstat, dummy handle encode/extract/validate, stale-handle mapping, and export root re-indexing.
