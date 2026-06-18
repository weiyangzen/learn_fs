# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_vfsops.c

## Purpose

Implements the illumos UDFS VFS layer: module registration, mount/unmount/root/statvfs/sync/vget/mountroot operations, UDF volume discovery, superblock construction/destruction, logical volume integrity conversion/update, VAT and sparing-table loading, logical-block-size discovery, and VFS/vnode operation registration.

## Main Entry Points

- `_init()`, `_fini()`, `_info()`: filesystem module lifecycle.
- `udf_mount()`: user mount entry, device/path resolution, permission checks, lofi support, mount option setup.
- `udf_unmount()`: flush and tear down mounted UDFS state.
- `udf_root()`, `udf_statvfs()`, `udf_sync()`, `udf_vget()`, `udf_mountroot()`: standard VFS operations.
- `ud_mountfs()`: common mount/remount/root-mount implementation.
- `ud_validate_and_fill_superblock()`: read anchor, volume descriptor sequence, partitions, maps, integrity sequence, file set descriptor, and root ICB.
- `ud_destroy_fsp()`: release all buffers, maps, partitions, mount strings, and list membership.
- `ud_convert_to_superblock()` / `ud_update_superblock()`: move logical volume integrity metadata into/out of `udf_vfs`.
- `ud_val_get_vat()`: locate and load virtual allocation table extents.
- `ud_read_sparing_tbls()`: load sparable partition replacement tables.
- `ud_get_lbsize()`: discover logical block size and anchor descriptor location.
- `udfinit()`: register VFS and vnode operation vectors and initialize inode globals.

## Control Flow And State

`udf_mount()` checks mount privilege, mountpoint validity/busy state, resolves the special device, accepts lofi-backed mounts, rejects already-mounted devices except remount, applies read-only/nosuid options, verifies device access, and calls `ud_mountfs()`.

`ud_mountfs()` opens the block device for initial mounts, rejects swap devices, handles read-only-to-read-write remounts by invalidating stale cached state and checking the logical volume integrity descriptor is closed, then discovers the block size with `ud_get_lbsize()` and builds `udf_vfs` through `ud_validate_and_fill_superblock()`. It enforces UDF 1.50 read/write limits, rejects writable mounts on non-overwritable media or virtual partition maps, checks domain write permissions, initializes locks, loads the root inode, links the mount into the global UDFS list, and marks writable mounts dirty.

`ud_validate_and_fill_superblock()` reads the anchor volume descriptor, main volume descriptor sequence with reserve fallback, chooses latest compatible primary/logical/partition descriptors, extracts partition space bitmap/table locations, validates domain IDs and block size, builds normal/virtual/sparable partition maps, reads the logical volume integrity sequence, imports free-block/file/dir/version counters, reads the file set descriptor through partition translation, and records the root ICB and root physical block.

VAT support searches near the last recorded block using configured offsets, validates a VAT file entry, supports embedded, short, and long allocation descriptors, and keeps buffers/address arrays pinned in the map. Sparing support validates packet length/table count, reads each sparing table, verifies the sparing table identifier, and retains valid table buffers for runtime remapping.

Unmount flushes non-root inodes, syncs root, writes a clean logical volume integrity descriptor for writable mounts, tears down locks and cache entries, releases the root vnode, frees `udf_vfs`, invalidates block-device pages/buffers, closes the device, and releases the device vnode. Forced unmount is explicitly unsupported.

## Dependencies

Depends on illumos VFS operation registration, vnode/specfs/lofi APIs, block and character device ioctl interfaces (`DKIOCGVTOC`, `DKIOCINFO`, `CDROMREADOFFSET`), descriptor verification, partition translation, inode cache, superblock sync helpers, and UDF volume descriptor definitions.

## Risks

The mount path is conservative and only supports UDF 1.50 for writes; newer read/write media features are rejected. `ud_get_last_block()` comments that the VTOC logic was known to work only on SPARC and needed x86 evaluation. VAT discovery relies on a small set of end-of-media offsets. Writable remount correctness depends on invalidating stale buffer/page/inode state before trusting the re-read integrity descriptor. Cleanup must release pinned VAT/sparing buffers to avoid leaking media metadata buffers.
