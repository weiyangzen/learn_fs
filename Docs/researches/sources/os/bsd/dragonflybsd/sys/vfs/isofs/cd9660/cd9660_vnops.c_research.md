# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_vnops.c

## Scope

Implements CD9660 vnode operations for read-only file access, attributes, directory iteration, symbolic links, block strategy, pathconf, advisory locks, and vnode operation tables.

## APIs And Behavior

- `cd9660_setattr()` rejects metadata and size changes for normal read-only objects while tolerating special-device size requests.
- `cd9660_access()` applies mount UID/GID overrides and file/directory masks before delegating to `vop_helper_access()`.
- `cd9660_getattr()` fills vnode attributes from `iso_node`, including symlink-size probing through RRIP readlink when recorded size is zero.
- `cd9660_ioctl()` supports `FIOGETLBA`.
- `cd9660_read()` performs block-sized reads with clustered read-ahead or `breadn()` depending on mount flags and sequential hints.
- `cd9660_readdir()` validates ISO directory records, translates names for ISO/Joliet/RRIP, supports directory cookies, and coalesces associated/default ISO entries in default mode.
- `cd9660_readlink()` extracts RRIP `SL` symbolic-link targets from the parent directory-record block.
- `cd9660_strategy()` maps logical offsets through `VOP_BMAP()` and sends I/O to the backing device vnode.
- Defines normal, special-device, and FIFO VOP tables.

## Dependencies

Depends on `cd9660_lookup()` and `cd9660_bmap()` from adjacent files, RRIP parsing, ISO name utilities, vnode pager, buffer clustering, lockf, FIFO ops, and DragonFly VOP infrastructure.

## Risks And Invariants

Directory parsing stops on malformed record lengths or block crossings. Symlinks require RRIP. All write-like mutation paths preserve read-only semantics. Strategy must complete the original bio if mapping fails or maps to `NOOFFSET`.
