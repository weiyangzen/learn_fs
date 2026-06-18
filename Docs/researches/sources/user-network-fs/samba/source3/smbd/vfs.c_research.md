# sources/user-network-fs/samba/source3/smbd/vfs.c

## Purpose
Provides smbd's VFS module registration/loading, per-file VFS extension storage, common file operation helpers, and dispatch wrappers for the full `vfs_fn_pointers` interface. It is the central bridge between SMB server logic and filesystem/module backends.

## Important APIs, Types, and Functions
Key module APIs include `smb_register_vfs()`, `vfs_init_custom()`, `smbd_vfs_init()`, and the backend list of `vfs_init_function_entry`. File extension APIs include `vfs_add_fsp_extension_notype()`, remove/fetch helpers, and extension destructors. Common helpers include range validation, `vfs_pwrite_data()`, allocation/truncation/sparse-fill helpers, `vfs_set_blocking()`, `vfs_readdirname()`, `vfs_ChDir_shareroot()`, `vfs_stat*()`, `vfs_fstreaminfo()`, `vfs_fake_fd()`, `vfs_at_fspcwd()`, and `vfs_get_fs_capabilities()`. The large `smb_vfs_call_*` block dispatches every VFS operation through the module stack, including async pread/pwrite/fsync, DOS attributes, xattrs, offload, durable handles, ACLs, snapshots, locks, and DFS operations.

## Control Flow
VFS initialization registers static backends if needed, loads the default backend, optionally adds `widelinks`, then loads configured `vfs objects` in reverse order so the first configured module becomes the outermost handler. Each dispatch wrapper uses `VFS_FIND()` to skip modules that do not implement the requested operation and panic if VFS calls are currently denied.

Write helpers validate offsets and lengths before invoking backend operations. `vfs_pwrite_data()` either drains unread request bytes through `SMB_VFS_RECVFILE()` with a blocking retry on EAGAIN/EWOULDBLOCK, or loops over `SMB_VFS_PWRITE()` until complete. Allocation helpers contend level2 oplocks around shrink/grow/zero-fill operations and use fallocate when possible. Async wrappers capture backend recv function pointers, install callbacks, translate backend errors into tevent Unix or NT errors, and return stored results through recv functions. Some async completion paths re-impersonate the file user before receiving backend results.

## State and Persistence
Process state includes the registered backend list, per-connection VFS handle chains, per-files_struct extension linked lists, the `chdir_lastconn_cache`, and a global VFS-deny stack pointer. Filesystem state is modified through backend calls for allocation, truncate, rename, ACL, xattr, durable-handle, and snapshot operations. The module parameter string is stored on the connection's talloc context.

## Dependencies and Integration Points
Depends on Samba module loading, loadparm share settings, `files_struct`, `connection_struct`, SMB filename/stat abstractions, oplock contention, notify, tevent, Unix I/O helpers, fd handles, memcache globals, and UID switching. Almost every smbd file operation reaches this layer through `SMB_VFS_*` macros.

## Risks
Module order is behavior-critical. `VFS_FIND()` assumes a later module implements every operation; developer builds can assert full function coverage, but production relies on stack correctness. Range validation must prevent overflow and invalid append-offset usage. Blocking retry in `vfs_pwrite_data()` must restore socket flags or request processing can be disrupted. Async completion paths assume `change_to_user_and_service_by_fsp()` succeeds and assert if it does not. Global `chdir_lastconn_cache` can become stale unless reset after cwd-affecting events.

## Test Signals
Test module registration version/name collisions, loading module paths with parameters, default/widelinks/configured order, per-fsp extension add/fetch/remove/destroy, pread/pwrite/allocation range boundaries, append mode, recvfile socket-drain behavior, fallocate fallback, truncate notifications, POSIX lstat behavior, fake fd behavior, fs capability/timestamp detection, VFS deny panic paths in developer tests, async pread/pwrite/fsync/xattr/DOS attribute error propagation, and representative wrapper calls across modules that implement/pass through operations.
