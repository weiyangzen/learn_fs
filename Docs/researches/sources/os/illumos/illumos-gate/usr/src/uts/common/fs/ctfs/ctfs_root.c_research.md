# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_root.c

## Purpose

`ctfs_root.c` is the central implementation file for the contract filesystem. It registers the ctfs module, creates VFS operations, builds vnode operation vectors for all ctfs node types, implements mount/unmount/root/statvfs, and provides common vnode helpers.

## File Shape

- Size: 521 lines, 12,422 bytes.
- SHA-256: `4406ef5d531f69c5abae939da321e15fdcd94a749d1aa50877fee468161eaf57`.
- Module entry points: `_init()`, `_info()`, `_fini()`.
- Defines global vnodeops pointers for root, all directory, symlink, type directory, template, contract directory, ctl, status, event, bundle, and latest nodes.
- Defines `ctfs_opsvec`, `ctfs_vfstops`, and `ctfs_tops_root`.
- Common exported helpers: `ctfs_common_getattr()`, `ctfs_open()`, `ctfs_close()`, `ctfs_access_dir()`, `ctfs_access_readonly()`, and `ctfs_access_readwrite()`.

## Core Behavior

- `ctfs_init()` registers VFS ops, builds all GFS vnode operation vectors with `gfs_make_opsvec()`, and allocates a unique major number.
- `ctfs_mount()` checks mount privilege and mountpoint suitability, allocates `ctfs_vfs_t`, assigns a unique device/minor, initializes VFS fields, dynamically builds the root directory entries from all registered contract types plus `all`, and creates the GFS root vnode.
- `ctfs_unmount()` checks privilege, rejects forced unmount, refuses unmount while the root vnode has active transitive holds, releases the root vnode, and frees VFS-private data.
- `ctfs_root()` returns a held root vnode.
- `ctfs_statvfs()` reports synthetic filesystem stats based on total contracts across all types, available/free file counts as `INT_MAX - total`, base type from `vfssw`, and filesystem string `contract`.
- `ctfs_common_getattr()` fills uid/gid/rdev/block accounting/fsid/nodeid fields common to all ctfs nodes.
- `ctfs_open()` enforces large-file-aware non-writable opens for directories and similar nodes.
- Access helpers implement directory read/execute only, read-only files, and read-write non-executable files.
- Root attributes report a read-only directory with entries for every contract type plus `all`.

## Dependencies And Contracts

- Uses GFS for synthetic directory/file mechanics and per-node operation vectors.
- Uses contract type registry globals `ct_types` and `ct_ntypes`.
- Uses CTFS inode macros to provide stable synthetic inode numbers.

## Maintenance Notes

The filesystem structure under `/system/contract` is public, but individual file behavior is private/unstable and expected to be accessed through libcontract. Adding new ctfs node types requires updating the ops vector definitions here as well as the relevant type-directory dirent construction in companion files.
