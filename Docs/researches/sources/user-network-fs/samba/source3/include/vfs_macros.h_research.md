# sources/user-network-fs/samba/source3/include/vfs_macros.h

## Purpose
`vfs_macros.h` provides the canonical `SMB_VFS_*` and `SMB_VFS_NEXT_*` invocation macros for source3 VFS operations. It hides direct access to `conn->vfs_handles`, `handle->next`, and `smb_vfs_call_*` wrapper details from callers and VFS modules.

## Important APIs, Types, and Macros
- Disk/quota/DFS: `SMB_VFS_CONNECT`, `DISCONNECT`, `DISK_FREE`, `GET_QUOTA`, `SET_QUOTA`, shadow copy, `FSTATVFS`, capabilities, and DFS referral/path calls.
- Directory: `FDOPENDIR`, `READDIR`, `REWINDDIR`, `MKDIRAT`, and `CLOSEDIR`.
- File operations: `OPENAT`, `CREATE_FILE`, `CLOSE`, sync/async `PREAD`/`PWRITE`, `LSEEK`, `SENDFILE`, `RECVFILE`, `RENAMEAT`, `RENAME_STREAM`, async `FSYNC`, stat variants, allocation, unlink, chmod/chown, timestamps, truncate/fallocate, locks, fcntl, leases, symlink/readlink/link/mknod, realpath, chflags, file IDs, streams, case lookup, byte-range locking, name translation, parent path, fsctl, DOS attributes, copy offload, compression, snapshots.
- Security/metadata: NT ACL, POSIX ACL fd/blob operations, xattr get/list/remove/set, AIO force, durable handle cookie/disconnect/reconnect, and readdir attributes.

## Control Flow and State
Each top-level macro starts dispatch at the connection's VFS stack, generally `conn->vfs_handles` or `fsp->conn->vfs_handles`. Each `NEXT` macro dispatches at `handle->next` for modules that intercept and delegate. This establishes the control-flow contract for stacked VFS modules.

## Persistence Behavior
The macros do not persist state, but many wrapped operations are persistence boundaries: file create/write/delete/rename, metadata mutation, ACL/xattr/quota changes, durable cookies, snapshots, and compression.

## Dependencies and Integration Points
The macros depend on `smb_vfs_call_*` declarations from `vfs.h` and on valid `connection_struct`, `files_struct`, and `vfs_handle_struct` relationships. They are included by `vfs.h`, so VFS callers and modules can use them uniformly.

## Risks
- Macro argument mistakes can dispatch through the wrong stack node or evaluate unexpected expressions.
- Module authors must call the `NEXT` variant when delegating; calling the top-level variant from inside a module can restart the stack and recurse.
- Some macros are long and easy to desynchronize from function signatures when `vfs_fn_pointers` changes.
- Because many macros derive connection from `fsp`, invalid or partially initialized `files_struct` values can crash before reaching wrapper validation.

## Test Signals
Build failures catch signature drift. Runtime signals include VFS module stacking tests, full-audit logging for each operation, durable/snapshot/xattr/ACL/quota module tests, and recursion/delegation tests for custom VFS modules.
