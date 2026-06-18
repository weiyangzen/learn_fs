# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_fat.c

Implements FAT block access, cluster-chain traversal, FAT cache lookup, cluster allocation/freeing, in-use bitmap construction, file extension, FAT mirroring, and FAT16/FAT32 dirty-bit updates.

Main responsibilities:
- `pcbmap()` maps file-relative clusters to filesystem-relative clusters and disk blocks.
- `fatentry()` reads and/or writes individual FAT entries.
- `clusteralloc()` finds and allocates contiguous free cluster runs.
- `freeclusterchain()` frees an entire cluster chain.
- `fillinusemap()` scans the FAT to build the in-memory allocation bitmap and free-cluster count.
- `extendfile()` appends allocated clusters to a denode’s chain and optionally clears them.
- `markvoldirty_upgrade()` manipulates FAT16/FAT32 clean/dirty volume bits.

Key implementation details:
- `fatblock()` maps FAT byte offsets to backing device blocks, with special FAT12 block-size adjustment for packed entries.
- `pcbmap()` handles fixed root-directory blocks separately from normal cluster chains and uses the denode FAT cache to avoid repeated full-chain scans.
- FAT12 reads/writes use packed 12-bit nibble logic; FAT16 uses 16-bit entries; FAT32 preserves high-order reserved bits.
- `updatefats()` mirrors modified FAT blocks to all FAT copies when mirroring is enabled, writing the primary/current FAT last.
- Allocation uses `pm_inusemap`, `pm_freeclustercount`, and `pm_nxtfree`; it prefers requested starts, then scans from next-free and wraps.
- `chainalloc()` marks bitmap bits first, writes the FAT chain, and rolls bitmap changes back on FAT write failure.
- `freeclusterchain()` updates both FAT entries and the in-use map under the msdosfs mount lock.
- `fillinusemap()` initially marks all clusters used, then frees entries whose FAT content is zero, validating cluster 0’s FAT media descriptor.
- `markvoldirty_upgrade()` skips FAT12, supports read-only-to-read-write upgrade, sets `B_INVALONERR`, and writes synchronously to avoid zombie dirty buffers on device write failure.

Important dependencies:
- Mount fields in `struct msdosfsmount`: FAT geometry, masks, bitmap, free counts, active FAT, mirroring flags, root-directory layout, and device vnode.
- Buffer cache and endian helpers from `bpb.h`.
- Denode cache helpers from `denode.h`.

Notable risks and edge cases:
- FAT12 packed entries are the most delicate path and require block sizing that safely spans adjacent bytes.
- Cluster 0 and 1 are special; generic `fatentry()` only accepts allocatable clusters, so dirty-bit code has a custom cluster-1 implementation.
- Freeing an already-free cluster reports an integrity error.
