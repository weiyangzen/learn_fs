# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_subr.c

Shared FFS helper routines for block access, fragment accounting, and free-block bitmap operations. The code is partly kernel-only and partly usable outside the kernel.

Key responsibilities:
- Implements `ffs_blkatoff()` to read the filesystem block containing a byte offset and optionally return a pointer to the in-buffer offset.
- Implements `ffs_blkatoff_ra()` with read-ahead or cluster-read behavior for sequential directory/file scans.
- Implements `ffs_fragacct()` to update cylinder-group fragment summary counts using the `fragtbl`, `around`, and `inside` lookup tables.
- Implements bitmap tests and mutations: `ffs_isblock()`, `ffs_isfreeblock()`, `ffs_clrblock()`, and `ffs_setblock()` for fragment configurations of 1, 2, 4, or 8 frags per block.

Dependencies:
- Kernel builds include vnode, buffer, credential, mount, quota, inode, filesystem, and FFS external interfaces.
- Non-kernel builds include `dinode.h` and `fs.h`, and provide a local `panic()` declaration.
- Uses tables defined in `ffs_tables.c` through `fs.h` externs.

Notable risks:
- Bitmap operations panic on unsupported `fs_frag` values, so superblock validation must ensure legal fragment geometry.
- `ffs_blkatoff_ra()` avoids readahead for the last block because it may be a fragment; callers depend on correct `i_size` and `blksize()` calculations.
- Fragment accounting is table-driven and sensitive to bit-pattern interpretation; mistakes corrupt free-space summaries.
