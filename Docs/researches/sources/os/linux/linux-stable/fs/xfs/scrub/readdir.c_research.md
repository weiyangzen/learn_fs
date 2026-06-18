# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/readdir.c

This file provides scrub-safe directory walking and lookup helpers.

Directory walking:
- `xchk_dir_walk` dispatches by XFS directory format:
  - shortform: `xchk_dir_walk_sf`
  - block: `xchk_dir_walk_block`
  - leaf/node: `xchk_dir_walk_leaf`
- Callers must hold ILOCK.
- Entries are reported through an `xchk_dirent_fn` callback with data position, name, inode number, and file type.

Format details:
- Shortform walking synthesizes `.` and `..`, then walks inline entries.
- Block walking reads the block directory buffer, skips free regions, computes entry sizes, and reports entries.
- Leaf/node walking scans mapped data blocks below `XFS_DIR2_LEAF_OFFSET`, reading only mapped data blocks and skipping holes/free entries.
- `xchk_read_leaf_dir_buf` uses the data fork extent map to find the next mapped directory data block.

Lookup:
- `xchk_dir_lookup` wraps `xfs_dir_lookup_args` with scrub transaction context.
- If looking up in a temporary directory, it adjusts the owner because temp directory block headers are written with the scrub target owner.

Parent-pointer locking:
- `xchk_dir_trylock_for_pptrs` repeatedly tries to lock scrub target and related parent inode in a deadlock-avoidant order.
- It uses nonblocking IOLOCKs because scrub can hold transactions.
- It returns `-EDEADLOCK` for normal retry, `-ETIMEDOUT` with incomplete flag under `TRY_HARDER`, and honors termination.

This file is a shared foundation for nlink collection, parent pointer validation, orphanage name selection, and parent repair scanning.
