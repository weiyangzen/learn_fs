# File Research: sources/os/linux/linux/fs/hostfs/hostfs_kern.c

Purpose: Implements the UML hostfs VFS layer, mapping Linux VFS operations inside UML to filesystem operations on the host path namespace.

Key functions:
- `hostfs_args()` parses early UML `hostfs=` boot options for root confinement and append mode.
- `dentry_name()` and `inode_name()` construct host paths by combining the configured host root with VFS dentry paths.
- `follow_link()` resolves a hostfs root symlink during mount setup.
- `hostfs_statfs()` fills VFS statfs data from host `statfs64`.
- Inode lifecycle functions allocate, initialize, evict, and free `hostfs_inode_info`, including host file descriptor cleanup.
- `hostfs_readdir()` opens the host directory, seeks to `ctx->pos`, reads host dirents, and emits them to VFS.
- `hostfs_open()` opens or upgrades a cached host fd for read/write mode under `open_mutex`.
- `hostfs_read_folio()`, `hostfs_write_begin()`, `hostfs_write_end()`, and `hostfs_writepages()` implement page-cache I/O through `read_file()`/`write_file()`.
- `hostfs_iget()` obtains or updates VFS inodes using host `statx` identity, including device and birth-time matching.
- Namespace operations create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, and rename host paths.
- `hostfs_permission()` delegates access checks to host `access()` for non-special files and then applies generic VFS permission.
- `hostfs_setattr()` maps VFS attributes to host chmod/chown/truncate/time operations.
- FS context functions parse mount parameters, set up a nodev superblock, and register `hostfs`.

Dependencies and integration:
- Consumes all host-side wrappers from `hostfs.h`.
- Uses VFS inode/file/address-space operations, fs_context parsing, dcache aliases, and UML setup hooks.

Risk notes:
- Host path construction is central security surface; root confinement depends on raw dentry path handling and configured `root_ino`.
- Append mode blocks unlink and truncation but still allows other host mutations.
- Cached fd mode upgrades use `dup2` replacement and shared inode state; concurrent opens are serialized with `open_mutex`.
- Hostfs does not cache dentries (`DCACHE_DONTCACHE`), reflecting the host namespace’s external mutability.
