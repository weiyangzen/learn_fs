# File Research: sources/os/linux/linux/fs/xfs/scrub/readdir.h

## Role
Declares directory walking and lookup helpers for scrub and repair.

## API
- `xchk_dirent_fn` is the callback signature for directory entries.
- `xchk_dir_walk` iterates all entries of a locked directory.
- `xchk_dir_lookup` resolves a name in a locked directory.
- `xchk_dir_trylock_for_pptrs` performs bounded locking for parent-pointer checks.

## Integration
Used by directory scrub, parent-pointer scrub/repair, nlink checks, and orphanage adoption.
