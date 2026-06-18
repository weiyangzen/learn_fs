# File Research: sources/os/linux/linux-stable/fs/afs/super.c

## Scope

Implements AFS filesystem registration, mount context parsing/validation, superblock creation/reuse, inode-cache management, and `statfs`.

## APIs And Behavior

- `afs_fs_init()` creates the vnode slab and registers the `afs` filesystem; `afs_fs_exit()` unregisters and destroys it.
- Mount parsing handles `source`, `dyn`, `autocell`, and `flock=` options, including `%`/`#` source prefixes and `.readonly`/`.backup` suffixes.
- `afs_validate_fc()` resolves the cell, gets a key, detects aliases, creates a volume, and forces read-only/local-locking behavior for RO/backup volumes.
- `afs_get_tree()` allocates `afs_super_info`, reuses matching superblocks, or fills new dynroot/volume superblocks.
- Inode slab hooks initialize/reset vnode locks, callback state, writeback key lists, directory/symlink cache pointers, and flags.
- `afs_statfs()` issues AFS/YFS get-volume-status operations for real volumes and returns fixed values for dynroot.

## State And Dependencies

Uses `struct file_system_type`, `super_operations`, fs-context private state, `afs_super_info`, volume/cell/key refs, dynroot helpers, root inode lookup, fscache activation, and netfs writeback integration.

## Risks And Invariants

Source parsing determines RW/RO/backup semantics that later affect server selection and mount writability. Superblock matching is by net namespace, cell, and volume ID. Inode reuse requires explicit reset of all non-static vnode state in `afs_alloc_inode()`.
