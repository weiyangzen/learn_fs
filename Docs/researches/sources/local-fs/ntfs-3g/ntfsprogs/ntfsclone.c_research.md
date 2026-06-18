# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsclone.c

## Role

Implements `ntfsclone`, a user-space NTFS cloning, imaging, restore, rescue, and metadata-only sanitization utility. It can clone used clusters to sparse files/devices/stdout, save/restore a compact special image format, rescue unreadable sectors, generate new volume serial numbers, adjust boot-sector sector-size fields, and create metadata-only images with optional timestamp/data wiping.

## Main Areas

- Option parsing validates mutually exclusive clone/restore/save-image/metadata/no-action/stdout combinations.
- Special image format handling defines the `\0ntfsclone-image` header, version 10.1, endian-safe fields, and command stream opcodes `CMD_GAP` and `CMD_NEXT`.
- I/O wrappers `io_all()`, `copy_cluster()`, `read_rescue()`, and `rescue_sector()` abstract device/file/stdin/stdout/image I/O and bad-sector rescue.
- Cluster discovery walks all in-use MFT records and attributes, decompresses mapping pairs, builds an internal LCN bitmap, and compares it with `$Bitmap`.
- Clone/restore paths use the bitmap or image command stream to copy allocated clusters and preserve gaps.
- Metadata mode identifies critical metadata clusters, handles `$LogFile` specially, includes the alternate boot sector, and can copy only selected metadata.
- Wiping mode clears resident user data, deleted/unused MFT record data, file-name/standard-information timestamps, directory index timestamps, and quota timestamps unless preservation is requested.
- Output setup handles sparse-file sizing, block-device size validation, free-space checks, sync, Windows-specific device output, and optional post-clone sector-size adjustment.

## Dependencies

Uses libntfs-3g volume, inode, attribute, bitmap, runlist, MST, boot sector, directory/index, timestamp, device, and utility APIs. It depends heavily on `ntfs_mount()`, `ntfs_inode_open()`, `ntfs_attrs_walk()`, `ntfs_mapping_pairs_decompress()`, `$Bitmap` reads, `ntfs_attr_pread()`, `ntfs_rl_pwrite()`, and MST fixup helpers.

## Important Behavior

The core correctness check is `compare_bitmaps()`: clusters discovered by walking metadata are compared against `$Bitmap`, and mismatches abort unless `--ignore-fs-check` is allowed for rescue/metadata situations. Bad clusters from `$BadClus` can be removed from the copy set.

The metadata-image path has two passes: first it computes metadata cluster usage, then it sets `wipe = 1` and emits wiped metadata records/clusters. MFT and `$I30` index allocations get record-level wiping so logical records spanning clusters are handled coherently.

The code intentionally preserves update sequence numbers when writing modified MFT records via `ntfs_mft_usn_dec()` before write/pre-write fixup. Restore validates image opcodes and bounds, and rejects metadata images to stdout when negative/invalid gaps imply non-linear placement.

## Research Notes

This is one of the highest-risk utilities in the group because it mixes filesystem metadata walking, raw cluster copying, image serialization, rescue reads, and direct metadata sanitization. The source also contains an endianness FIXME and special compatibility handling for pre-10.0 images.
