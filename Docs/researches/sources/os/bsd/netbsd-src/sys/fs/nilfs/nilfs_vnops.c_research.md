# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_vnops.c

Implements vnode operations for NILFS files and directories.

Key points:
- Lifecycle:
  - `nilfs_inactive()` is mostly passive.
  - `nilfs_reclaim()` destroys genfs state and disposes the NILFS node.
- Read path:
  - `nilfs_read()` validates vnode type and uses `ubc_uiomove()` against the vnode UVM object.
  - `nilfs_vfsstrategy()` maps vnode buffers to device I/O through `nilfs_read_filebuf()`.
  - `nilfs_read_filebuf()` translates logical blocks to virtual blocks, then virtual to physical blocks, issuing nested device buffers; holes are zero-filled.
- Mapping:
  - `nilfs_trivial_bmap()` returns NILFS virtual block mappings and contiguous run length.
  - A virtual block of zero is returned as `-1` to signal unmapped/hole behavior.
- Directory operations:
  - `nilfs_readdir()` walks NILFS directory entries and emits NetBSD `dirent` records.
  - `nilfs_lookup()` handles `.`, `..`, namecache lookup, dirhash-backed lookup, vnode-cache creation, and negative/create lookup behavior.
- Metadata:
  - `nilfs_getattr()` maps NILFS inode fields to `vattr`.
  - `nilfs_access()` uses generic vnode authorization after read-only and type checks.
  - `nilfs_pathconf()` reports NILFS limits.
- Mutation paths:
  - `nilfs_write()` contains a hard `panic("nilfs_write() called")`.
  - Strategy writes panic through `nilfs_write_filebuf()`.
  - create, mknod, mkdir, link, symlink, rename, remove, and rmdir route to helper stubs that generally return `EROFS` or cannot succeed.
  - `readlink()` returns `EROFS`.

Risk/notes:
- The vnode table advertises many operations, but the practical implementation is read-oriented.
- Write attempts are unsafe in some paths because they panic rather than returning an error.
