# File Research: sources/local-fs/btrfs-progs/mkfs/main.c

## Role

`mkfs/main.c` is the main implementation of the `mkfs.btrfs` command. It parses user options, validates feature/profile/device combinations, prepares target devices or image files, creates the initial Btrfs trees and block groups, optionally populates the new filesystem from `--rootdir`, and finalizes the filesystem by cleaning temporary chunks, initializing optional roots, discarding free space, and fixing the on-disk signature on close.

## Main Data Structures

- `struct mkfs_allocation` tracks allocated byte totals for data, metadata, mixed, system, and remap block groups so verbose output can report final allocation profiles.
- `struct prepare_device_progress` carries per-device preparation state into `pthread_create()` workers, including fd, path, requested size, discovered size, and return status.
- Global option state:
  - `opt_zero_end`: whether preparation zeros the device end.
  - `opt_discard`: whether whole-device and free-space discard are attempted.
  - `opt_zoned`: whether zoned mode is enabled.
  - `opt_oflags`: open flags shared by device-preparation threads.

## Key Control Flow

`BOX_MAIN(mkfs)` is the command entry point.

1. Initializes CPU/hash/config feature machinery.
2. Parses options for profiles, features, label, UUIDs, node/sector sizes, `--rootdir`, subvolumes, inode flags, compression, reflink, shrink, discard, verbosity, and experimental parameters.
3. Applies defaults:
   - sectorsize defaults to 4 KiB.
   - nodesize defaults to max(sectorsize, default node size).
   - profile defaults depend on single-device vs multi-device and mixed-bg mode.
4. Validates option combinations:
   - `--rootdir` is single-device only.
   - `--shrink`, `--reflink`, `--subvol`, `--inode-flags`, and `--compress` require `--rootdir`.
   - zoned mode rejects `--rootdir`, mixed-bg, and RAID5/6.
   - remap-tree rejects mixed-bg and zoned mode.
   - extent-tree-v2/remap-tree force no-holes, free-space-tree, and block-group-tree dependencies.
5. Canonicalizes `source_dir` and validates requested rootdir subvolumes and inode-flag paths through `rootdir.c`.
6. Checks device overwrite safety, UUID validity, minimum size, RAID profile feasibility, and zoned profile support.
7. Prepares devices in parallel with `prepare_one_device()`.
8. Calls `make_btrfs()` to create the initial on-disk filesystem.
9. Opens the filesystem with write/temporary-super/exclusive flags.
10. Creates metadata/system/default data chunks, optional RAID stripe/remap/global roots, and the initial root directory.
11. Adds additional devices, creates final RAID-profile block groups, commits, and re-COWs existing trees into the final profiles.
12. Creates the data relocation tree unless remap-tree is enabled.
13. If `--rootdir` is set, calls `btrfs_mkfs_fill_dir()` to populate the filesystem, then optionally calls `btrfs_mkfs_shrink_fs()`.
14. Rebuilds the UUID tree, removes temporary chunks, initializes quota roots if requested, prints verbose summary, discards free space, sets `finalize_on_close`, and closes the ctree.

## Important Functions

- `create_metadata_block_groups()` allocates initial system, metadata/mixed, and optional remap block groups. It handles zoned system group sizing and records allocation totals.
- `create_data_block_groups()` creates the initial data block group unless mixed block groups are enabled.
- `make_root_dir()` creates the root-tree directory object, the fs-tree root directory, and the root-tree `"default"` dir item/ref.
- `__recow_root()`, `recow_global_roots()`, and `recow_roots()` walk tree leaves and force COW of tree blocks so metadata moves from temporary chunks into final-profile chunks.
- `create_one_raid_group()` and `create_raid_groups()` allocate profile-specific system, metadata/mixed, and data block groups.
- `zero_output_file()` initializes a regular output image by zeroing the first MiB and extending it to the target size.
- `list_all_devices()` prints a sorted device table, including zone counts in zoned mode.
- `is_temp_block_group()`, `next_block_group()`, and `cleanup_temp_chunks()` identify and remove empty temporary single-profile chunks after final chunks exist.
- `discard_logical_range()`, `queue_discard_logical()`, `discard_all_devices()`, and `discard_free_space()` translate logical free-space ranges to device ranges and submit discard, skipping RAID56 mappings.
- `update_chunk_allocation()` recomputes allocation totals from block-group cache after rootdir population may have allocated extra chunks.
- `create_global_root()` and `create_global_roots()` create extra extent/csum/free-space roots for extent-tree-v2 global roots.
- `setup_quota_root()` creates and initializes qgroup/simple-quota metadata, then runs qgroup verification and repair to fill accounting.
- `setup_raid_stripe_tree_root()` and `setup_remap_tree_root()` create optional feature roots and wire them into fs_info/super fields.
- `prepare_one_device()` is the thread callback that opens and prepares each target using `btrfs_prepare_device()`.
- `parse_compression()` recognizes `no`, `zlib[:level]`, `lzo[:level]`, and `zstd[:level]`, subject to compile-time support and level limits.
- `parse_subvolume()` parses `--subvol` entries into `rootdir_subvol` records, including default and read-only modes.
- `parse_inode_flags()` parses comma-separated `nodatacow` and `nodatasum` flags for a `FLAGS:PATH` option.

## Dependencies and Interactions

This file is tightly integrated with Btrfs shared code:

- Tree and transaction operations from `kernel-shared/ctree.h`, `disk-io.h`, `transaction.h`, `volumes.h`, and `zoned.h`.
- Feature parsing and validation from `common/fsfeatures.h`.
- Device probing/preparation from `common/device-utils.h` and `common/device-scan.h`.
- Rootdir population and sizing from `mkfs/rootdir.h`.
- Quota verification from `check/qgroup-verify.h`.
- Profile parsing, minimum size logic, and low-level mkfs creation from `mkfs/common.h`.

`main.c` delegates the content-copying complexity to `rootdir.c`; its responsibility is to ensure the target filesystem is sized, created, and opened correctly before rootdir import.

## Notable Invariants

- `--rootdir` only supports one target device and is rejected with zoned mode.
- Mixed block groups require matching data and metadata profiles.
- Remap-tree requires no-holes/free-space-tree/block-group-tree and cannot be combined with mixed-bg or zoned mode.
- Extent-tree-v2 requires at least one global root and forces dependent features.
- Finalization is delayed until the filesystem is fully built; `finalize_on_close` is set only at the end.
- Temporary block groups are removed only if empty and if their profile does not match the final mkfs profile.
- RAID56 free-space discard is skipped because mapping/discard semantics are unsafe for this path.

## Error Handling

The file consistently reports negative errno-style errors through `error()`/`error_msg()`, aborts transactions on setup failures where needed, and converts final command status to boolean shell exit status. Some fatal validation paths call `exit(1)` directly. Transaction commit failures are reported with the shared transaction error message macro.

## Research Notes

This is the orchestration layer for mkfs. Most Btrfs metadata details are in shared helpers, but `main.c` defines the exact command behavior, feature compatibility matrix, initial tree/chunk construction sequence, temporary-to-final profile migration, rootdir integration point, and final cleanup sequence.
