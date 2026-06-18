# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_subr.c

Provides shared FFS helper routines usable in kernel and some userland contexts.

Key entry points:
- `ffs_bufatoff()` reads a directory block for a byte offset and returns an optional pointer within it.
- `ffs_fragacct()` updates fragment summary counts for a block map.
- `ffs_isblock()`, `ffs_clrblock()`, `ffs_setblock()`, and `ffs_isfreeblock()` manipulate full-block availability in fragment bitmaps.
- `ffs_vinit()` initializes vnode type/op vectors and handles device aliases.

Important behavior:
- Bitmap helpers specialize for `fs_frag` values 1, 2, 4, and 8.
- `ffs_fragacct()` uses `fragtbl`, `around`, and `inside` patterns to count available fragment runs.
- `ffs_bufatoff()` adjusts buffer count to the actual logical block size from `blksize()`.
- `ffs_vinit()` assigns spec/fifo vop tables, marks root vnode, and initializes `i_modrev`.

Dependencies:
- Kernel part depends on UFS inode/vnode structures, buffer cache, and FFS vop tables.
- Non-kernel part exposes fragment and bitmap helpers plus `panic()` prototype for userland filesystem tools.

Watch points:
- The bitmap routines assume valid `fs_frag`; invalid fragment counts are rejected earlier by mount validation.
