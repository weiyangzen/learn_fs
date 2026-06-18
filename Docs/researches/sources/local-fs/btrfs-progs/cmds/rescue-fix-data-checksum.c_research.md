# File Research: sources/local-fs/btrfs-progs/cmds/rescue-fix-data-checksum.c

## Purpose

Implements `btrfs rescue fix-data-checksum`, a specialized offline tool that scans checksum items, verifies all mirrors for each checksummed data sector, reports logical blocks with checksum/read failures, resolves affected filenames, and optionally updates checksum items from a selected mirror.

## Main API

- `int btrfs_recover_fix_data_checksum(const char *path, enum btrfs_fix_data_checksum_mode mode, unsigned int mirror)`
- Modes come from `cmds/rescue.h`:
  - readonly report only
  - interactive prompt per corrupted logical block
  - noninteractive checksum update from a selected mirror

## Control Flow

1. Checks mount status and refuses mounted filesystems.
2. Opens the ctree with `OPEN_CTREE_WRITES`.
3. Rejects running replace or balance operations.
4. Gets the checksum root and walks all `BTRFS_EXTENT_CSUM_KEY` items.
5. For each checksummed sector, `verify_one_data_block()` reads every mirror and compares computed checksum with the csum item bytes.
6. Corrupted logical blocks are accumulated in global `corrupted_blocks`.
7. `report_corrupted_blocks()` prints affected logical bytenrs, failed mirror numbers, paths resolved through backrefs, and applies the selected repair action.
8. `update_csum_item()` starts a transaction, reads the chosen mirror, recomputes the checksum, overwrites the csum item, and commits.

## State

- `struct corrupted_block` records logical bytenr, mirror count, and a bitmap of failed mirrors.
- `corrupted_blocks` is a global list freed at command exit.
- `global_repair_mode` is assigned but not used later in this file.

## Dependencies

Uses checksum root helpers, data mirror reads, inode backref/path resolution, transaction helpers, mount-status checks, and shared rescue mode declarations.

## Risks And Edge Cases

- In `add_corrupted_block()`, the duplicate-last-entry path calls `set_bit(mirror, ...)`, while the new-entry path uses `set_bit(mirror - 1, ...)`; this looks like an off-by-one bug for repeated corruption records.
- `verify_one_data_block()` continues to checksum `buf` after `read_data_from_disk()` fails, so a failed read can be followed by a checksum comparison against stale or undefined data.
- `iterate_one_csum_item()` allocates `buf` but never uses it.
- `update_csum_item()` has an error format typo: `"failed to find csum item for logical %llu: $m"`.
- Updating checksum items is dangerous when the selected mirror is itself stale or corrupt; the tool trusts the user or requested mirror.
