# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_vnops.c

## Purpose
Implements vnode operations for NetBSD FilecoreFS, a read-only Acorn FileCore filesystem implementation. It maps Filecore nodes into generic VFS behavior for permission checks, attributes, reads, directory iteration, block mapping/strategy, and pathconf.

## Main Entry Points
- `filecore_access()` enforces read-only semantics for regular files, directories, and symlinks, then delegates permission checks to `kauth_authorize_vnode()` and `genfs_can_access()`.
- `filecore_getattr()` fills `vattr` from `filecore_node` and mount defaults for uid/gid, size, timestamps, mode, and block size.
- `filecore_read()` reads regular files through UBC and non-regular/directory-backed content through `bread()` or `filecore_dbread()`.
- `filecore_readdir()` emits synthetic `.` and `..` entries, converts FileCore names with `filecore_fn2unix()`, and optionally returns cookies.
- `filecore_strategy()` resolves logical-to-physical mappings through `VOP_BMAP()` and forwards I/O to the underlying device vnode.
- `filecore_pathconf()` reports read-only filesystem limits such as one link, 256 path max, and 32 file-size bits.
- `filecore_vnodeop_entries` wires unsupported mutation operations to `genfs_eopnotsupp` or read-only helpers.

## Dependencies
Uses NetBSD VFS/vnode, UBC, buffer cache, kauth, genfs, specfs, and Filecore-specific node/mount helpers from `filecore.h`, `filecore_extern.h`, and `filecore_node.h`.

## Risks and Notes
The implementation is explicitly read-only. `filecore_readlink()` returns `EINVAL`, so symlink targets are not supported despite symlink-related checks elsewhere. Directory cookies are allocated based on remaining user buffer size; the code advances the local `cookies` pointer before assigning it back, so callers receive the advanced pointer rather than the original allocation base. `filecore_readdir()` relies on `filecore_fn2unix()` to signal directory end or invalid entries, and older in-source comments note a type mismatch around `d_namlen`.
