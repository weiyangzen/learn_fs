# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/hfs_vnops.c

## Purpose
Implements HFS/HFS+ vnode operations for lookup, attributes, read access, readdir, block mapping, reclaim, and operation-vector registration. Mutation operations are mostly unsupported, making the filesystem read-only.

## Main Entry Points
- `hfs_vnodeop_entries`, `hfs_specop_entries`, and `hfs_fifoop_entries` define regular, special, and fifo vnode operation tables.
- `hfs_vop_parsepath()` delegates to `genfs_parsepath()` and extends parsing for `/rsrc` resource fork suffixes, though the table currently uses `genfs_parsepath` directly.
- `hfs_vop_lookup()` checks execute access, handles `.` and `..`, converts path components from UTF-8 to UTF-16, maps `:` and `/`, searches the catalog via `libhfs`, follows HFS+ hardlink metadata, and chooses data or resource fork vnode.
- `hfs_vop_access()` rejects writes to regular files, directories, and symlinks, then authorizes based on `VOP_GETATTR()` results.
- `hfs_vop_getattr()` translates catalog records into `vattr`, including fork size, block usage, BSD metadata, timestamps, type, uid/gid/mode defaults, and special-device numbers.
- `hfs_vop_setattr()` rejects most changes with `EINVAL`, `EROFS`, `EISDIR`, or `EOPNOTSUPP`.
- `hfs_vop_bmap()` asks `libhfs` for file extents, maps logical allocation blocks to underlying device blocks, and reports run length.
- `hfs_vop_read()` reads regular files and symlinks through UBC up to the selected fork logical size.
- `hfs_vop_readdir()` loads directory children with `hfslib_get_directory_contents()`, converts UTF-16 names to UTF-8, maps `/` to `:`, emits `dirent` records, and frees temporary arrays.
- `hfs_vop_readlink()` delegates symlink content reads to `VOP_READ()`.
- `hfs_vop_reclaim()` releases the device vnode, destroys genfs state, and returns the node to the pool.

## Dependencies
Uses NetBSD vnode/genfs/specfs/fifofs/UBC interfaces, HFS node structures, `libhfs`, and local UTF conversion helpers from `unicode.h`.

## Risks and Notes
The operation table wires `vop_parsepath` to `genfs_parsepath`, so the custom `/rsrc` parser is not active in the table as shown. `..` lookup uses `HFS_RSRCFORK`, which is surprising for parent directory lookup. `hfs_vop_bmap()` returns `EBADF` for zero extents, so zero-length files need careful handling. `hfs_vop_readdir()` sets EOF on partial entry rather than true end and does not update `uio_offset` explicitly after emitting entries. Debug output references `curchildname`, which is not defined unless hidden by debug configuration. Name conversion error paths are mostly TODO comments.
