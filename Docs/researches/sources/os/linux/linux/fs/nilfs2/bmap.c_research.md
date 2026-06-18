# File Research: sources/os/linux/linux/fs/nilfs2/bmap.c

`bmap.c` implements the common NILFS2 block mapping layer. It wraps direct and B-tree mapping implementations behind `nilfs_bmap_operations`, handles conversion between small direct maps and large B-trees, translates virtual block numbers through DAT, serializes operations with the bmap semaphore, and normalizes corruption errors.

Core behavior:
- `nilfs_bmap_get_dat()` returns the filesystem DAT inode.
- `nilfs_bmap_convert_error()` turns internal `-EINVAL` corruption signals into `-EIO` after reporting a broken bmap with inode number.
- Lookup functions call the active mapping operation under read lock. `nilfs_bmap_lookup_at_level()` also translates virtual block numbers to physical block numbers through DAT and treats missing DAT entries as corruption.
- Insert/delete functions call check hooks that can trigger representation conversion: direct-to-B-tree on insert growth, B-tree-to-direct on delete shrink.
- `nilfs_bmap_truncate()` repeatedly deletes the last key until all keys at or above the requested key are gone.
- Clear, propagate, dirty-buffer lookup, assign, and mark delegate to operation-table hooks under appropriate locking.
- Dirty state is tested and cleared atomically with the write lock.
- `nilfs_bmap_data_get_key()` maps a buffer head position back to a bmap key.
- Target selection helpers use sequential locality or inode-number-derived DAT group locality.

Initialization:
- `nilfs_bmap_read()` loads raw on-disk bmap data, initializes locking/state, selects pointer type by metadata inode number, assigns lockdep classes for DAT/metadata bmaps, and initializes either B-tree or direct mode based on the `NILFS_BMAP_LARGE` flag.
- DAT uses physical pointers; checkpoint/sufile use single-version virtual pointers; ifile and regular files use multi-version virtual pointers.
- `nilfs_bmap_write()` copies the in-memory bmap back to the raw inode and resets DAT’s last allocated pointer marker.
- `nilfs_bmap_init_gc()` initializes a GC-only bmap with pointer operations disabled and B-tree GC ops.
- Save/restore copies raw data, last allocation hints, and dirty state.

This file is the polymorphic control layer for NILFS block addressing and metadata relocation.
