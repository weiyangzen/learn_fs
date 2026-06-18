# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_fat.c

## Scope

Implements FAT block addressing, FAT chain traversal, FAT cache maintenance, FAT entry mutation, cluster allocation/freeing, free-space map initialization, file extension, and FAT clean/dirty bit updates.

## APIs And Behavior

- `fatblock()` maps a FAT byte offset to backing-device block, size, and byte offset.
- `pcbmap()` maps file-relative clusters to filesystem blocks or clusters, handles fixed FAT12/16 root directories, walks FAT chains, normalizes reserved/EOF markers, and updates denode FAT cache.
- `fc_lookup()` and `fc_purge()` manage per-denode FAT cache entries.
- `updatefats()` writes modified FAT blocks, mirroring to secondary FATs when configured and preserving clean bits in mirrored copies.
- `fatentry()` gets, sets, or get-and-sets one FAT12/16/32 entry.
- `fatchain()` writes a contiguous chain into FAT entries.
- `chainlength()`, `chainalloc()`, `clusteralloc()`, and `clusteralloc1()` allocate contiguous free cluster runs using the in-use bitmap and next-free hint.
- `clusterfree()` and `freeclusterchain()` free one cluster or an entire chain and update the in-use map.
- `fillinusemap()` scans FAT entries to build free cluster state and validate FAT media descriptor.
- `extendfile()` appends cluster chains to a denode and optionally clears new clusters.
- `markvoldirty_upgrade()` sets or clears FAT16/FAT32 volume clean bits.

## Dependencies

Uses MSDOSFS mount geometry/macros, buffer I/O, endian helpers, denode locks, and mount lock assertions.

## Risks And Invariants

FAT12 nibble packing is handled specially and is easy to corrupt if offsets cross blocks incorrectly. Use-map mutation requires the mount lock. Allocation updates the bitmap before FAT writes but rolls back on failure. FAT32 high entry bits must be preserved.
