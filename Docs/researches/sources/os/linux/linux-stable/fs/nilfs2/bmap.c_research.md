# File Research: sources/os/linux/linux-stable/fs/nilfs2/bmap.c

Purpose: implements the common NILFS2 block-map wrapper that sits above direct and btree mapping backends. It handles lookup, insert, delete, truncate, dirty propagation, block assignment, conversion between direct and btree formats, DAT virtual-block translation, and bmap initialization/save/restore.

Key structures and state:
- `struct nilfs_bmap` stores raw inode bmap data, an rwsem, owner inode, operation table, last allocation target key/ptr, pointer type, dirty state, and children-per-block geometry.
- Operation dispatch uses `struct nilfs_bmap_operations` supplied by direct or btree implementations.
- Pointer type controls whether records are physical block numbers, single-version virtual block numbers, multi-version virtual block numbers, or unmanaged GC pointers.
- Static lockdep classes distinguish DAT bmap locking from metadata-file bmap locking.

Major logic:
- `nilfs_bmap_lookup_at_level()` dispatches backend lookup and, for virtual-block bmaps, translates the virtual block through DAT to a physical block; missing DAT entries are treated as bmap corruption.
- Insert checks whether a direct map must convert to btree, gathers existing direct data, calls btree conversion/insert, and sets the `NILFS_BMAP_LARGE` flag on success.
- Delete checks whether a btree can convert back to direct, gathers btree data, performs delete/convert, and clears the large flag on success.
- Truncate repeatedly deletes the current last key until all keys greater than or equal to the cutoff are gone.
- Clear, propagate, dirty-buffer lookup, assign, mark, seek-key, and last-key all delegate to backend operations under appropriate locking.
- Dirty state is tested and cleared atomically under the bmap write semaphore.
- Target helpers derive sequential allocation guesses from the last allocated key/ptr or distribute targets by inode number within a DAT allocation group.
- `nilfs_bmap_read()` initializes bmap raw data from an on-disk inode, sets pointer type based on special inode number, initializes lockdep class, and selects direct versus btree backend from the on-disk large flag.
- `nilfs_bmap_write()` copies bmap raw data back to the on-disk inode and resets DAT allocation target state.
- GC bmaps are initialized as unmanaged btree-style maps with pointer type `NILFS_BMAP_PTR_U`.
- Save/restore copies raw bmap data plus allocation target and dirty state into/from a shadow store.

Concurrency and lifetime:
- Read operations take `b_sem` for read; mutating operations take it for write.
- Backend conversion and mutation are serialized by the common bmap semaphore.
- Dirty-buffer lookup intentionally calls the backend without taking the common semaphore in this wrapper.
- Error conversion reports `-EINVAL` as filesystem corruption and maps it to `-EIO`.

Important dependencies:
- Depends on NILFS direct maps, btrees, DAT translation, btnode, allocator, metadata files, and core NILFS inode/superblock structures.
- Supplies the mapping layer used by NILFS regular files and metadata files.

Risk/edge cases:
- A bmap record whose virtual block has no DAT translation is treated as corrupted metadata.
- Direct/tree conversion thresholds must match constants in `bmap.h`, direct, and btree code.
- Last-key-driven truncate can be expensive for large maps but preserves backend invariants.
- Pointer-type selection for special metadata inodes is central to correct DAT versus metadata behavior.
