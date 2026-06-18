# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_tables.c

This file defines static lookup tables for FFS fragment allocation accounting.

Key responsibilities:
- Provide bit masks used to identify available fragment runs inside a block bitmap byte.
- Provide fragment availability tables for filesystems with 1, 2, 4, or 8 fragments per block.
- Export the `fragtbl` pointer array indexed by `fs_frag`.

Important data:
- `around[9]`: Masks used when scanning fragment bit patterns.
- `inside[9]`: Expected interior bit patterns for available fragments.
- `fragtbl124[256]`: Availability table shared by fragment counts 1, 2, and 4.
- `fragtbl8[256]`: Availability table for 8 fragments per block.
- `fragtbl[MAXFRAG + 1]`: Selects the appropriate table for `fs_frag`.

Important interactions:
- Used by `ffs_fragacct` and allocation scanning code via external declarations.
- Encodes historic FFS fragment rules, including VAX `scanc`-oriented table use described in comments.

Notable behavior and risks:
- Entries for unsupported fragment counts are null; callers must use validated `fs_frag` values.
- This file has no executable functions; correctness depends on table constants matching FFS bitmap semantics.
