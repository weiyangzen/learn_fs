# File Research: sources/local-fs/btrfs-linux/fs/btrfs/file-item.h

## Purpose

Declares the Btrfs file extent item and checksum helper interface implemented by `file-item.c`, plus inline helpers for inline file extent sizing and addressing.

## Key Definitions

- `BTRFS_FILE_EXTENT_INLINE_DATA_START` is the byte offset inside `struct btrfs_file_extent_item` where inline payload data begins.
- `BTRFS_MAX_INLINE_DATA_SIZE()` computes the maximum inline payload that fits in a leaf item.
- `btrfs_file_extent_inline_item_len()` returns the on-disk inline payload length, excluding the file extent header.
- `btrfs_file_extent_inline_start()` returns the address of inline payload data within a file extent item.
- `btrfs_file_extent_calc_inline_size()` returns total item size for a given inline data size.

## Public API Surface

The header exposes checksum deletion, checksum lookup for bios/ranges/bitmaps, checksum insertion, bio checksum generation, dummy ordered sum allocation, explicit hole extent insertion, file extent lookup, extent item to extent-map conversion, inode file-extent coverage tracking, safe disk i_size updates, and file extent end calculation.

## Integration Points

It includes Btrfs tree definitions, ordered-data declarations, and core ctree declarations, while forward-declaring most heavier structures. It is used by file IO, extent mapping, logging, checksumming, encoded IO, direct/buffered write paths, and metadata update paths that need file extent item semantics.

## Invariants And Risks

- Inline extent helpers encode on-disk layout assumptions; changes to `struct btrfs_file_extent_item` layout must keep these helpers consistent.
- `BTRFS_MAX_INLINE_DATA_SIZE()` depends on leaf item sizing and therefore filesystem node/leaf geometry.
- Callers of the declared mutation APIs must provide correct transaction/path locking and sectorsize-aligned ranges where required by `file-item.c`.
