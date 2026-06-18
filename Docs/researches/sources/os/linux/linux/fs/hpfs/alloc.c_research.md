# File Research: sources/os/linux/linux/fs/hpfs/alloc.c

Purpose: Implements HPFS sector and dnode allocation/freeing, bitmap accounting, allocation checks, and filesystem trim/discard.

Key functions:
- `hpfs_claim_alloc()`, `hpfs_claim_free()`, `hpfs_claim_dirband_alloc()`, and `hpfs_claim_dirband_free()` maintain cached free counts, invalidating them on underflow/overflow.
- `hpfs_chk_sectors()` validates sector ranges and, in strict check mode, verifies allocation bitmap state.
- `alloc_in_bmp()` searches and updates a 4-sector bitmap for 1-sector or 4-sector allocations near a target.
- `hpfs_alloc_sector()` implements HPFS allocation strategy: near target, current bitmap, surrounding bitmaps, then reduced forward preallocation.
- `alloc_in_dirband()` allocates dnodes from the dedicated directory band bitmap.
- `hpfs_alloc_if_possible()` opportunistically claims a specific free sector.
- `hpfs_free_sectors()` frees sector runs and updates main bitmap/free count.
- `hpfs_check_free_dnodes()` verifies enough free dnodes are available before directory tree mutations.
- `hpfs_free_dnode()`, `hpfs_alloc_dnode()`, `hpfs_alloc_fnode()`, and `hpfs_alloc_anode()` manage initialized on-disk structures.
- `hpfs_trim_fs()` scans free bitmap runs and issues block discard requests, including directory-band free dnodes.

Dependencies and integration:
- Uses bitmap mapping helpers from `map.c`/`buffer.c`, HPFS superblock counters, dnode band metadata, and global HPFS locking for trim.
- Supplies allocation primitives to dnode, anode, EA, file, and namespace creation code.

Risk notes:
- HPFS bitmaps use inverted semantics: 1 means free, 0 means allocated.
- Directory dnodes are 4-sector aligned and may come from a separate directory band.
- Several paths assume `n` is only 1 or 4 sectors.
- Trim loops can be interrupted by pending fatal signals.
