# File Research: sources/local-fs/ntfs-3g/libntfs-3g/device.c

## Role

Implements low-level device abstraction helpers, positioned I/O wrappers, MST-protected record I/O, cluster I/O, device sizing, geometry queries, sector-size queries, and block-size setup.

## Main Functions

- `ntfs_device_alloc()` allocates and initializes an `ntfs_device`.
- `ntfs_device_free()` frees a closed device and rejects open devices with `EBUSY`.
- `ntfs_device_sync()` syncs only when the device dirty flag is set.
- `ntfs_pread()` and `ntfs_pwrite()` wrap device operation callbacks and loop until the requested byte count completes, errors, or EOF/short write occurs.
- `ntfs_mst_pread()` reads fixed-size records and applies MST post-read fixups.
- `ntfs_mst_pwrite()` applies MST pre-write fixups, writes records, then deprotects the caller buffer with post-write fixups.
- `ntfs_cluster_read()` and `ntfs_cluster_write()` translate LCN/count to byte offsets using volume cluster size and enforce volume bounds.
- `ntfs_device_size_get()` obtains device size using platform ioctls where available, falling back to binary probing with seek/read.
- `ntfs_device_partition_start_sector_get()` queries partition start sector via `HDIO_GETGEO` when supported.
- `ntfs_device_heads_get()` and `ntfs_device_sectors_per_track_get()` retrieve cached or probed legacy geometry.
- `ntfs_device_sector_size_get()` uses Linux, FreeBSD, or macOS sector-size ioctls.
- `ntfs_device_block_size_set()` sets block size when supported, treating non-block devices as success.

## Dependencies

Uses device operations from `device.h`, MST fixups from `mst.h`, NTFS type/layout helpers, and many platform-specific headers/ioctls gated by configure macros.

## Important Behavior

`ntfs_pwrite()` rejects writes on read-only devices with `EROFS`, marks the device dirty before writing, and if synchronous mode is enabled, converts a sync failure after data was written into a partial-write result. Cluster writes on read-only volumes simulate success by returning the requested cluster count without calling the device write path.

MST write intentionally mutates the caller buffer temporarily, then restores it after the write. This matches NTFS-3G’s cache convention that in-memory records remain deprotected.

## Research Notes

This file is the base I/O substrate for higher-level metadata code. `index.c` and `dir.c` use MST attribute I/O for index blocks; `compress.c` ultimately relies on these lower layers through attribute and cluster reads/writes.
