# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_exclave_fs.c

## Scope

This file implements the VFS-backed exclave filesystem bridge. It registers APFS base directories by filesystem tag, tracks open vnodes by file id, supports graft inode translation, exposes open/create/read/write/remove/sync/readdir/getsize/sealstate operations, and includes development-only ENOSPC injection.

## Public And Internal APIs Covered

- Lifecycle: `vfs_exclave_fs_start()` and `vfs_exclave_fs_stop()`.
- Registration: `vfs_exclave_fs_register()`, `vfs_exclave_fs_register_path()`, `vfs_exclave_fs_unregister()`, `vfs_exclave_fs_get_base_dirs()`.
- Exclave root/file operations: `vfs_exclave_fs_root()`, `vfs_exclave_fs_root_ex()`, `vfs_exclave_fs_open()`, `vfs_exclave_fs_create()`, `vfs_exclave_fs_close()`.
- I/O and metadata: `vfs_exclave_fs_read()`, `vfs_exclave_fs_write()`, `vfs_exclave_fs_remove()`, `vfs_exclave_fs_sync()`, `vfs_exclave_fs_readdir()`, `vfs_exclave_fs_getsize()`, `vfs_exclave_fs_sealstate()`.
- Internal helpers manage registered tags, open-vnode counts, APFS graft info, inode mapping, base-directory creation, and vnode attributes.

## Control Flow And Behavior

Startup initializes two mutexes, an open-vnode hash sized from `desiredvnodes`, and a registered-tag hash. Registration accepts only APFS directories, queries graft metadata, rejects writable tags on grafts, refs the base vnode, probes root-auth for sealed state on read-only tags, and installs a `registered_fs_tag_t`.

Writable filesystem tags are `EFT_EXCLAVE` and `EFT_EXCLAVE_MAIN`. Root lookup for writable tags rejects path-like exclave IDs, opens the per-exclave root directory, and creates it if missing. `exclave_fs_open_internal()` resolves paths under either the registered base directory or an already-open root vnode, optionally deletes before create to avoid inode reuse, calls `vn_open_auth()`, translates graft inode numbers when needed, and increments the open-vnode table.

Read/write build a single-segment kernel `uio` and call `VNOP_READ()` or `VNOP_WRITE()`. Writes are rejected for non-writable tags, and development/debug builds can force `ENOSPC` for configured exclaves. Close decrements the open table and calls `vn_close()`. Remove delegates to `unlink1()`. Sync maps exclave sync operations to `F_BARRIERFSYNC`, `F_FULLFSYNC`, or `VNOP_FSYNC()`.

`vfs_exclave_fs_readdir()` uses `VNOP_GETATTRLISTBULK()` to produce packed `exclave_fs_dirent_t` records. For `EFT_SYSTEM`, release builds reject VFS directory enumeration, while development/debug builds allow it only if integrity checks are disabled or the base is not sealed.

## State And Data Structures

- `registered_fs_tag_t` stores fs tag, flags, base vnode, device id, and optional APFS graft info.
- `open_vnode` records vnode, device, host file id, fs tag, open count, and debug flags.
- Global hashes are protected by `regtag_mtx` and `open_vnodes_mtx`.
- Graft mapping translates between root inode `2`, APFS graft directory id, and the graft inode range.

## Dependencies

Depends on XNU VFS namei/open/vnode APIs, APFS graft ioctls (`FSIOC_GET_GRAFT_INFO`, `FSIOC_EVAL_ROOTAUTH`), `unlink1()` from VFS syscalls, attrlist bulk directory enumeration, devfs/fsevents headers, PE boot arguments, and kernel allocation/locking primitives.

## Risks And Invariants

- Base-directory registration forbids nested registered ancestors; this prevents ambiguous roots.
- Open-vnode refcounts must balance `vnode_ref()`/`vnode_rele()` and `vnode_getwithref()`/`vnode_put()` across register, open, close, unregister, and stop paths.
- Graft inode translation must be applied in the correct direction: API-facing file ids are graft ids, while open-table keys are host ids.
- `release_open_vnodes()` drops all vnode refs for a tag during unregister, regardless of external clients that may still think file ids are open.
- Create deletes an existing file before opening with `O_EXCL` to avoid inode reuse; the attack window is explicitly handled by adding `O_EXCL`.
- `vfs_exclave_fs_readdir()` has a direct `return ENOBUFS` before common cleanup when `eofflag` is false, which is a notable resource-lifetime edge.
