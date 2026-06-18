# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/readdir.h

This header declares scrub directory utilities.

It defines:
- `xchk_dirent_fn`: callback signature for directory entry walkers.
- `xchk_dir_walk`: iterate all entries in a directory.
- `xchk_dir_lookup`: exact name lookup in a directory.
- `xchk_dir_trylock_for_pptrs`: coordinated locking helper for parent-pointer validation.

The callback provides scrub context, directory inode, directory data position, XFS name, child inode number, and caller-private data.
