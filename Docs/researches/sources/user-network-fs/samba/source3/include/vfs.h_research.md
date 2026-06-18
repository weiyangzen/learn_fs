# sources/user-network-fs/samba/source3/include/vfs.h

## Purpose
`vfs.h` is the central source3 VFS ABI and file-server state header. It defines the VFS interface version, core file/connection/request/path structures, operation function-pointer table, module handle state, VFS extension helpers, public `smb_vfs_call_*` wrappers, registration APIs, and not-implemented fallback declarations.

## Important APIs, Types, and Constants
- ABI constant: `SMB_VFS_INTERFACE_VERSION 53`, with an extensive version history documenting every VFS ABI change.
- Core state: `files_struct`, `connection_struct`, `smb_request`, `smb_filename`, `stream_struct`, `smb_file_time`, `vfs_aio_state`, `vfs_open_how`, `vfs_rename_how`, `fsp_lease`, and `vuid_cache`.
- Function table: `struct vfs_fn_pointers` covers disk, quota, DFS, directory, open/create/close, sync/async read/write/fsync, stat, metadata mutation, locking, share modes, leases, symlink/link/mknod, realpath, file IDs, copy offload, compression, snapshots, streams, case lookup, byte-range locking, name translation, fsctl, DOS attributes, NT ACLs, POSIX ACLs, xattrs, AIO, durable handles, and readdir attributes.
- Module handle: `vfs_handle_struct` links modules in a stack and stores module-private data and cleanup callback.
- Extension/data helpers: `VFS_ADD_FSP_EXTENSION`, `VFS_FETCH_FSP_EXTENSION`, `VFS_MEMCTX_FSP_EXTENSION`, `VFS_REMOVE_FSP_EXTENSION`, and `SMB_VFS_HANDLE_*`.
- Public wrappers: `smb_vfs_call_*` declarations correspond to VFS macro calls and function pointers.
- Registration/assertion: `smb_register_vfs`, `smb_vfs_assert_all_fns`, `smb_vfs_assert_allowed`, and VFS deny push/pop.
- Fallbacks: `vfs_not_implemented_*` declarations for unimplemented module operations.

## Control Flow and State
The VFS call path is stacked. High-level code uses `SMB_VFS_*` macros from `vfs_macros.h`, which call `smb_vfs_call_*` with `conn->vfs_handles` or `handle->next`. The wrappers dispatch through `vfs_fn_pointers`, allowing modules to intercept operations and then delegate to the next module. `files_struct` carries per-open state, including access masks, fd handles, oplocks/leases, delete-on-close, byte-range lock cache, pathref/FSA flags, stream relationships, async requests, and SMB1 lock-blocking state. `connection_struct` carries per-tree/share state, VFS stack, session info, share capabilities, hide/veto lists, encryption state, and current directory handle.

The pathref/FSA commentary is critical: `is_pathref` marks low-level handles that may be O_PATH or root-opened fallback references and are restricted to descriptor/path operations, while `is_fsa` marks handles processed through Samba's NTFS-semantic file system abstraction. Callers must use `fsp_get_pathref_fd` for metadata/path operations and `fsp_get_io_fd` for true I/O.

## Persistence Behavior
The header defines persistence boundaries for filesystem mutation and durable state: create/open, write, rename, unlink, timestamps, allocation, quota, xattrs, DOS attributes, NT/POSIX ACLs, durable handle cookies, snapshots, compression, and DFS paths. It does not implement persistence itself; VFS modules and wrappers do.

## Dependencies and Integration Points
`vfs.h` includes `smbprofile.h` and then `vfs_macros.h`, and depends on many Samba types: security descriptors, SMB leases/create blobs, talloc, tevent, quota types, stat types, DFS referrals, byte-range locks, TDB-backed open state, and readdir attributes. It is used by smbd request handlers, VFS modules, ACL/quota/EA/stream code, durable-handle code, and file-serving subsystems.

## Risks
- This is an ABI header. Adding/removing/reordering `vfs_fn_pointers` requires bumping the interface version and updating audit/full-audit modules and default wrappers.
- Pathref misuse is security-sensitive: calling I/O or mutating operations on root-opened/O_PATH handles can bypass intended permission semantics or fail unpredictably.
- Module stack delegation must use `NEXT` calls correctly to avoid recursion, bypassing lower modules, or skipping default behavior.
- `files_struct` and `connection_struct` fields are central concurrent server state; incorrect lifetime or talloc ownership can create stale handles, bad leases, lock leaks, or delete-on-close bugs.
- Async VFS operations require exact send/recv pairing and correct `vfs_aio_state` propagation.

## Test Signals
VFS module ABI build tests, full-audit operation coverage, SMB create/open/read/write/rename/unlink/lock/oplock/durable-handle torture tests, pathref-specific permission tests, xattr/ACL/quota tests, async I/O tests, snapshot/compression/offload tests, and module-stack delegation tests are all relevant.
