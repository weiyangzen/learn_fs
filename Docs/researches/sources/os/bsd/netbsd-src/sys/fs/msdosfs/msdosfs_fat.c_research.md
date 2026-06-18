# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_fat.c

## Summary
Implements FAT block mapping, FAT cache maintenance, FAT entry reads/writes, FAT mirroring, free-space bitmap construction, cluster allocation/freeing, and file-chain extension for NetBSD msdosfs. It is the core allocator and logical-cluster-to-physical-sector translation layer for FAT12, FAT16, and FAT32.

## Main Responsibilities
- Map file-relative clusters to filesystem-relative sectors through `msdosfs_pcbmap()`, with special handling for fixed-size FAT12/16 root directories.
- Maintain denode FAT cache entries via `msdosfs_fc_lookup()` and `msdosfs_fc_purge()` to avoid repeated FAT-chain scans.
- Read and update FAT entries through `msdosfs_fatentry()`, preserving FAT32 high bits and handling packed FAT12 entries.
- Propagate FAT writes to mirrored FAT copies and update FAT32 FSInfo free-count/next-free hints in `updatefats()`.
- Track allocation state in `pm_inusemap` and `pm_freeclustercount` with `usemap_alloc()`, `usemap_free()`, and `msdosfs_fillinusemap()`.
- Allocate contiguous cluster chains with `chainlength()`, `chainalloc()`, and `msdosfs_clusteralloc()`, using a pseudo-randomized scan start for new files.
- Free clusters through `msdosfs_clusterfree()` and `msdosfs_freeclusterchain()`.
- Extend file chains through `msdosfs_extendfile()`, including optional zeroing for newly allocated directory clusters.

## Key Interfaces
- `msdosfs_pcbmap(struct denode *, u_long, daddr_t *, u_long *, int *)`.
- `msdosfs_fatentry(int, struct msdosfsmount *, u_long, u_long *, u_long)`.
- `msdosfs_clusteralloc(struct msdosfsmount *, u_long, u_long, u_long *, u_long *)`.
- `msdosfs_clusterfree(struct msdosfsmount *, u_long, u_long *)`.
- `msdosfs_freeclusterchain(struct msdosfsmount *, u_long)`.
- `msdosfs_fillinusemap(struct msdosfsmount *)`.
- `msdosfs_extendfile(struct denode *, u_long, struct buf **, u_long *, int)`.

## Risks
The file directly mutates FAT metadata and the allocation bitmap, so partial failures can desynchronize in-memory allocation state from on-disk FAT entries; for example, `chainalloc()` marks clusters allocated before `fatchain()` succeeds and does not roll back on `fatchain()` error. FAT12 packed-entry handling is offset-sensitive, and bounds checks around FAT block offsets are critical. `updatefats()` ignores FSInfo write errors after disabling future FSInfo updates, and FAT mirroring writes other copies before the primary/current FAT. Several recovery comments note crash-consistency limitations typical of non-journaled FAT.
