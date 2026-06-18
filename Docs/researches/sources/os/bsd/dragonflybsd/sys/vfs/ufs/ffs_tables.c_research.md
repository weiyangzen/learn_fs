# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_tables.c

Static fragment-pattern lookup tables used by FFS free-space accounting and allocation logic.

Key responsibilities:
- Defines `around[]` and `inside[]` bit masks used to identify available fragments inside a block map.
- Defines `fragtbl124` for filesystems with 1, 2, or 4 fragments per block.
- Defines `fragtbl8` for filesystems with 8 fragments per block.
- Exposes `fragtbl[MAXFRAG + 1]`, mapping legal fragment counts to the appropriate table and unsupported counts to null.

Dependencies:
- Includes only `sys/param.h`.
- Consumed by `ffs_fragacct()` and any code using `fragtbl` through `fs.h`.

Notable risks:
- These constants encode on-disk bitmap semantics; changing values would alter allocator behavior and summary accounting.
- Unsupported fragment counts deliberately have null table entries, so callers must validate or restrict `fs_frag`.
