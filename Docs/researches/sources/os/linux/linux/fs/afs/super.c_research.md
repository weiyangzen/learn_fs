# File Research: sources/os/linux/linux/fs/afs/super.c

## Scope

This file registers the `afs` filesystem, parses mount options/source syntax, validates mount contexts, creates/reuses superblocks, manages AFS inode slab objects, and implements `statfs`.

## Public And Internal APIs Covered

- Filesystem lifecycle: `afs_fs_init()` and `afs_fs_exit()`.
- `afs_fs_type` and `afs_super_ops`.
- Mount context operations: parameter parsing, `afs_get_tree()`, and context cleanup.
- Inode lifecycle: slab initialization, `afs_alloc_inode()`, `afs_destroy_inode()`, `afs_free_inode()`.
- Superblock display/stat: device-name/options display and `afs_statfs()`.

## Control Flow And Behavior

- Initialization creates `afs_inode_cache` and registers the filesystem. Exit unregisters, verifies no active inodes remain, runs an RCU barrier, and destroys the cache.
- Source parsing accepts AFS mount syntax such as `%cell:volume`, `#cell:volume`, `.readonly`, `.backup`, and `none` for dynroot.
- Mount validation requires a cell and key for non-dynroot mounts, performs alias detection when needed, creates a volume, and forces RO mounts/local flock mode for non-RW volumes.
- `sget_fc()` reuses matching non-dynroot superblocks by net namespace, cell, and volume ID, or dynroot superblocks by net namespace.
- `afs_fill_super()` initializes basic superblock fields, xattr handlers, BDI, root inode/dentry, dentry operations, and volume activation.
- `afs_kill_super()` clears `volume->sb` before killing the anon superblock, then deactivates volume cache state and frees super info.
- `afs_statfs()` reports fixed dynroot values or issues a get-volume-status operation.

## State And Data Structures

- `struct afs_super_info` stores net namespace, flock mode, dynroot flag, cell, and volume.
- `struct afs_fs_context` stores parsed mount state, selected cell/volume/key, volume type, force flag, and options.
- `struct afs_vnode` slab initialization sets locks, lists, callback work, writeback key list, and validation state.

## Dependencies

- Linux fs_context, superblock, inode slab, net namespace, netfs, fscache through volume activation, AFS volume/cell/key code, dynroot, dentry ops, and xattrs.

## Risks And Invariants

- `source=none` is valid only with `dyn`.
- Non-RW volumes are mounted read-only and use local flock semantics.
- Reused superblocks must already be active.
- Inode allocation must reset fields that can leak from slab reuse.
