# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_alloc.c

FAT cluster allocation, deallocation, logical-to-physical mapping, and in-core FAT entry manipulation for illumos PCFS.

Key responsibilities:
- Implements `pc_bmap()` for read-side logical cluster to disk block translation, including contiguous-byte discovery and FAT12/FAT16 fixed root-directory special casing.
- Implements `pc_balloc()` for write-side allocation and no-hole extension of file or directory cluster chains.
- Implements `pc_bfree()` for truncation/removal of cluster chains after a retained prefix.
- Counts free clusters through `pc_freeclusters()`, using FAT32 FSInfo cached counts when valid.
- Reads and writes FAT12, FAT16, and FAT32 entries through `pc_getcluster()` and `pc_setcluster()`, including FAT32 high-nibble preservation and FAT12 packed 12-bit entry handling.
- Allocates clusters in `pc_alloccluster()`, optionally zero-filling newly allocated clusters with direct buffer I/O.
- Provides `pc_fileclsize()` to count cluster-chain length and detect loops by bounding traversal by filesystem cluster count.

Dependencies:
- Relies on `pcfs` geometry and FAT state from `pc_fs.h`, directory/node metadata from `pc_dir.h` and `pc_node.h`, buffer cache I/O, endian conversion helpers, and FAT dirty tracking via `pc_mark_fat_updated()`.
- Assumes callers hold the PCFS filesystem lock and have a resident FAT for cluster operations.

Notable risks:
- Corrupt FAT chains are treated as filesystem damage and may mark the instance bad or irrecoverable.
- FAT12 packed-entry updates can span FAT change-map blocks, so dirty tracking must include both affected blocks.
- `pc_alloccluster()` scans from `pcfs_nxfrecls` to the end only; after frees, `pc_setcluster()` resets the next-free hint to `PCF_FIRSTCLUSTER`.
- File size is FAT-limited and cluster-chain traversal is bounded to prevent infinite loops on damaged media.
