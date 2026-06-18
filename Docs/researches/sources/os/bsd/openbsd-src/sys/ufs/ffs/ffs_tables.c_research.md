# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_tables.c

Defines static fragment-allocation lookup tables used by FFS allocation and accounting.

Contents:
- `around[]` and `inside[]` bit masks support testing whether a fragment run of a given size is available.
- `fragtbl124[]` covers fragment configurations 1, 2, and 4.
- `fragtbl8[]` covers 8 fragments per block.
- `fragtbl[]` maps supported `fs_frag` values to the correct lookup table and leaves unsupported values NULL.

Important behavior:
- Allocation code uses these tables with bitmap scans to quickly locate suitable fragment runs.
- Mount validation rejects `fs_frag` values whose `fragtbl` entry is NULL.

Dependencies:
- Used by `ffs_mapsearch()` and `ffs_fragacct()` through declarations in FFS headers.
