# File Research: sources/local-fs/ntfs-3g/ntfsprogs/mkntfs.c

## Role

`mkntfs.c` is the complete NTFS volume creation utility. It formats a target block device or forced regular file as NTFS 3.1, lays out boot sectors and metadata files, builds the initial MFT, root directory, `$Extend` contents, indexes, security descriptors, allocation bitmaps, and optionally a volume object id.

## Main Structures And State

- `struct mkntfs_options opts` stores command-line state: device, label, quick/no-action/force flags, geometry overrides, sector/cluster sizes, MFT zone multiplier, epoch-time mode, and UUID request.
- Global buffers and runlists hold transient format state: `g_buf` for initial MFT records, `g_mft_bitmap`, dynamic bitmap/log write buffer, runlists for `$MFT`, `$MFTMirr`, `$LogFile`, `$Boot`, `$BadClus`, and allocation bookkeeping.
- `struct BITMAP_ALLOCATION` models allocated cluster runs before the on-disk `$Bitmap` is written.
- `struct UPCASEINFO` is the Windows 8-era `$UpCase:$Info` payload containing a CRC64 of the upcase table.

## Control Flow

1. `main()` sets logging and locale, initializes options, parses CLI, then calls `mkntfs_redirect()` when parsing returns "proceed".
2. `mkntfs_parse_options()` handles formatter options, logging options, help/version/license, device and optional sector count. It returns tri-state status: success-done, error, or proceed.
3. `mkntfs_redirect()` owns the formatting pipeline:
   - allocates `ntfs_volume`, sets NTFS 3.1 version, label, cluster size, attrdef, upcase table, and `$UpCase:$Info` CRC;
   - opens and validates the target with `mkntfs_open_partition()`;
   - computes geometry and NTFS sizing in `mkntfs_override_vol_params()`;
   - initializes allocation bitmaps and runlists for `$MFT`, `$MFTMirr`, `$LogFile`, `$Boot`, and `$BadClus`;
   - optionally zero-fills the volume;
   - creates metadata records in `mkntfs_create_root_structures()`;
   - syncs root index, `$Bitmap`, `$MFT`, `$MFTMirr`, and the device.

## Formatting And Metadata Creation

- Device validation refuses non-block devices and whole disks unless `--force` is set; it checks mounted status through `ntfs_check_if_mounted()`.
- Geometry defaults are inferred through libntfs device helpers, with fallback warnings for sector size, partition start, heads, and sectors per track.
- Cluster size defaults to 4096 bytes, grows for very large volumes, must be power-of-two, at least sector size, not over NTFS maximum, and not too large for Windows compression.
- MFT record size defaults to 1024 bytes and index record size to 4096 bytes, raised to sector size if needed.
- `$Bitmap` allocation is first represented in memory through `bitmap_allocate()`, `bitmap_deallocate()`, `bitmap_get_and_set()`, and `bitmap_build()`, then streamed to disk with `WRITE_BITMAP`.
- `$LogFile` contents are synthesized as `0xff` bytes through `WRITE_LOGFILE`.
- `mkntfs_create_root_structures()` builds 27 system records, including `$MFT`, `$MFTMirr`, `$LogFile`, `$Volume`, `$AttrDef`, root directory, `$Bitmap`, `$Boot`, `$BadClus`, `$Secure`, `$UpCase`, `$Extend`, reserved files, `$Quota`, `$ObjId`, and `$Reparse`.
- Boot sector construction fills BPB geometry, MFT locations, record-size encodings, serial number, checksum, and writes a backup boot sector.
- Security descriptors are initialized through helper functions from `security.h`; `$Secure` gets `$SDS`, `$SDH`, and `$SII`.
- `$Quota`, `$ObjId`, and `$Reparse` are built as view-index system files below `$Extend`.

## Attribute And Index Helpers

- The file includes local versions of attribute lookup/find logic tailored for formatting, with attribute-list support mostly unsupported outside simple paths.
- `insert_resident_attr_in_mft_record()`, `insert_non_resident_attr_in_mft_record()`, and `insert_positioned_attr_in_mft_record()` create attributes and write non-resident data via runlists.
- `add_attr_*` wrappers create standard information, file names, object ids, security descriptors, data streams, volume name/info, index root/allocation, and bitmaps.
- Directory and view indexes are built with simplified insertion logic suitable for initial filesystem creation, not a general-purpose mutable NTFS index implementation.
- `upgrade_to_large_index()` converts root `$I30` from resident-only index root into a large index with `$BITMAP` and `$INDEX_ALLOCATION`.

## Important Dependencies

This file relies heavily on libntfs-3g internals: device I/O, endianness wrappers, MFT layout, mapping pairs, MST fixups, NTFS names/collation, boot-sector validation, security descriptor initialization, upcase table generation, and logging.

## Notable Limitations And Risk Areas

- Many comments explicitly mark incomplete functionality: compressed attributes, sparse/encrypted attribute insertion, attribute-list/extent handling, making attributes non-resident, robust index algorithms, bad-block persistence, and full boot/log exactness.
- The formatter has broad global mutable state, so partial failures depend on `mkntfs_cleanup()` for memory/device cleanup and may leave a partially formatted target.
- `opts.no_action` bypasses writes in several helpers, but most structures are still constructed in memory.
- The code intentionally uses simplified index lookup/insertion because it creates a fresh filesystem. Reusing these helpers as general NTFS mutation code would be unsafe.
- The volume is marked dirty if backup boot sector creation fails, relying on Windows chkdsk to recreate it later.

## External Interface

CLI syntax is `mkntfs [options] device [number-of-sectors]`. Major options include quick format, label, compression/indexing defaults, no-action, cluster/sector geometry, partition start, MFT zone multiplier, epoch time, UUID, force, verbosity, version, license, and help.
