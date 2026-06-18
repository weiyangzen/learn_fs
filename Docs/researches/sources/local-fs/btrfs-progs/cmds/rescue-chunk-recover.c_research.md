# File Research: sources/local-fs/btrfs-progs/cmds/rescue-chunk-recover.c

## Purpose

Implements `btrfs rescue chunk-recover` backend. It reconstructs a damaged chunk tree by scanning all devices for valid Btrfs tree blocks, extracting surviving chunk/block-group/device-extent metadata, deriving missing chunk records, validating reconstructed mappings against filesystem metadata, and finally rewriting the chunk tree, system chunk array, and missing block-group items.

## Main API

- `int btrfs_recover_chunk_tree(const char *path, int yes)` is the exported rescue entry point declared in `cmds/rescue.h`.
- Internal state is centered on `struct recover_control`, which owns recovered metadata caches, device set, checksum/super geometry, and chunk classification lists:
  - `chunk`, `bg`, `devext`, `eb_cache`
  - `good_chunks`, `bad_chunks`, `rebuild_chunks`, `unrepaired_chunks`
  - `rc_lock` for multithreaded scan insertion

## Control Flow

1. `recover_prepare()` opens the input device, reads a recovery-mode superblock, rejects seed devices, records sectorsize/nodesize/generation/checksum details, and scans all filesystem devices.
2. `scan_devices()` starts one pthread per device. `scan_one_device()` walks the device at node-size intervals, skips superblock bytenrs, verifies fsid and tree-block checksum, records newest matching tree blocks, and extracts metadata leaf items from extent/dev/chunk trees.
3. `check_chunks()` reconciles chunk, block-group, and device-extent records into good/bad/rebuild lists. If orphan block groups or device extents remain, `btrfs_recover_chunks()` creates synthetic chunk records from block groups and orphan device extents.
4. Stripe recovery uses metadata location for ordered metadata RAID chunks and checksum-guided matching for data RAID chunks.
5. `open_ctree_with_broken_chunk()` builds an in-memory mapping tree from recovered good/rebuild chunk records so normal metadata can be read.
6. Metadata cross-checks run through `check_all_chunks_by_metadata()` and `btrfs_rebuild_ordered_data_chunk_stripes()`.
7. After confirmation, a write transaction removes old system chunk extent items, rebuilds the chunk root, inserts device and chunk items, rebuilds the system array, and inserts missing block-group items.

## Notable Algorithms

- Newer duplicate records replace older generation records during scan insertion.
- `btrfs_rebuild_ordered_meta_chunk_stripes()` maps tree-block logical addresses to expected stripe indexes to recover stripe order for stripey metadata chunks.
- `rebuild_raid_data_chunk_stripes()` attempts to identify data stripe ordering by comparing checksum tree entries against candidate device extents.
- `validate_rebuild_chunks()` rejects rebuilt chunks that overlap already-good chunks.

## Dependencies

Uses btrfs-progs shared libraries for tree access, transactions, volume mapping, chunk/block-group/device-extent record creation, checksum validation, extent buffers, and cache trees. It also reuses `check_chunks()` and shared block-group/device extent structures from checker code.

## Risks And Edge Cases

- The final repair phase uses `BUG_ON()` after transaction start for several failures, so unexpected write-side errors can abort rather than unwind cleanly.
- `check_one_csum()` contains `UASSERT(0)` and initializes `csum_size` to zero before comparing checksums; this is suspicious because RAID data stripe recovery calls it.
- `calculate_bg_used()` tests `BTRFS_EXTENT_DATA_KEY` while walking the extent tree, where extent items are expected as `BTRFS_EXTENT_ITEM_KEY` or `BTRFS_METADATA_ITEM_KEY`; this can undercount block-group used bytes.
- The recovery scan is raw-device and sector/node stepping based; false negatives are possible if metadata is not aligned as expected or only older generations remain.
- RAID56 data stripe order recovery has explicit limitations for parity-based inference.
