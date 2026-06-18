# File Research: sources/local-fs/btrfs-progs/cmds/rescue.h

## Purpose

Small shared header for rescue command backends.

## API

Defines `enum btrfs_fix_data_checksum_mode`:

- `BTRFS_FIX_DATA_CSUMS_READONLY`
- `BTRFS_FIX_DATA_CSUMS_INTERACTIVE`
- `BTRFS_FIX_DATA_CSUMS_UPDATE_CSUM_ITEM`
- `BTRFS_FIX_DATA_CSUMS_LAST`

Declares:

- `btrfs_recover_superblocks()`
- `btrfs_recover_chunk_tree()`
- `btrfs_recover_fix_data_checksum()`

## Dependencies And Role

Used by `rescue.c`, `rescue-super-recover.c`, `rescue-chunk-recover.c`, and `rescue-fix-data-checksum.c` to share backend entry points without exposing implementation details.

## Risks

No internal logic. ABI risk is limited to changing enum values or function signatures used across rescue translation units.
