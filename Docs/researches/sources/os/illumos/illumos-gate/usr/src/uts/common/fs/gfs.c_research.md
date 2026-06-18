# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/gfs.c

## Role

Provides Generic File System support for in-kernel pseudo-filesystems. It offers reusable vnode creation, directory lookup/readdir, inactive cleanup, vnodeops creation, and read-only mmap support.

## Main Behavior

- `gfs_make_opsvec()` builds multiple vnodeops vectors and unwinds prior creations on failure.
- Low-level readdir helpers:
  - `gfs_get_parent_ino()` resolves parent/self inode numbers.
  - `gfs_readdir_init()` allocates reusable dirent/edirent state and validates offsets.
  - `gfs_readdir_emit()` and `gfs_readdir_emitn()` emit named or numeric entries.
  - `gfs_readdir_pred()` handles `.` and `..` and calculates virtual offsets.
  - `gfs_readdir_fini()` frees state and reports EOF.
- `gfs_lookup_dot()` handles empty name, `.`, and `..`.

## Managed GFS Objects

- `gfs_file_create()` allocates private data and vnode, initializes parent relationship, vnode ops, type/vfs/dev, and parent hold.
- `gfs_dir_create()` extends file creation for directories with static entries, dynamic callbacks, inode callback, max name length, and directory lock.
- `gfs_root_create()` and `gfs_root_create_file()` create VFS-rooted directory/file vnodes with `VROOT`, `VNOCACHE`, `VNOMAP`, `VNOSWAP`, and `VNOMOUNT`.

## Lookup And Readdir

- `gfs_dir_lookup_static()` searches static entries, optionally constructs and caches vnodes, resolves races where another thread caches first, and supports case-insensitive real-name output.
- `gfs_dir_lookup_dynamic()` calls a filesystem callback outside the directory lock, then annotates GFS vnode metadata.
- `gfs_dir_lookup()` combines dot, static, and dynamic lookup, including case-conflict detection via `ED_CASE_CONFLICT`.
- `gfs_dir_readdir()` emits static entries and dynamic callback entries through common readdir state.

## Cleanup And Mapping

- `gfs_file_inactive()` removes cached static references, handles xattrdir parent state, releases parent or VFS references, and frees vnode if refcount permits.
- `gfs_dir_inactive()` also destroys directory locks and static entry storage.
- `gfs_vop_inactive()`, `gfs_vop_lookup()`, and `gfs_vop_readdir()` are direct vnode op adapters.
- `gfs_vop_map()` supports read-only mmap by creating a zero-fill-on-demand mapping, then filling it through `vn_rdwr()`; it rejects executable/writable mappings.

## Dependencies And Interactions

- Used by pseudo-filesystems that place `gfs_file_t` or `gfs_dir_t` first in `v_data`.
- Interacts with VFS feature flags for case behavior and vnode extended attribute directory state.
