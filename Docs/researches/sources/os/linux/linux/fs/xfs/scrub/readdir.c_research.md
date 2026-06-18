# File Research: sources/os/linux/linux/fs/xfs/scrub/readdir.c

## Role
Provides scrub-side directory iteration, directory lookup, and parent-pointer lock helpers.

## Directory Walking
- `xchk_dir_walk` dispatches by directory format.
- `xchk_dir_walk_sf` synthesizes `.` and `..` entries and iterates shortform entries.
- `xchk_dir_walk_block` reads block-format directories and reports non-free data entries.
- `xchk_dir_walk_leaf` scans mapped data blocks below the leaf offset for leaf/node directories.

## Lookup
- `xchk_dir_lookup` performs exact name lookup using XFS directory args and returns the target inode number.
- For repair temp directories, it substitutes the scrub target as owner because temp directory block headers use that owner.

## Lock Helper
- `xchk_dir_trylock_for_pptrs` attempts to lock scrub target and peer inode with IOLOCK/ILOCK ordering suitable for uncertain/corrupt directory trees.
- It returns success, retry/deadlock, timeout with `INCOMPLETE` under `TRY_HARDER`, or interruption.

## Assumptions
- Callers must hold the directory ILOCK for walking and lookup.
- Callback file types are XFS directory filetype values.
