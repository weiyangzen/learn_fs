# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_exchmaps.c

## Purpose

`xfs_exchmaps.c` implements the libxfs side of exchanging mapping ranges between two inode forks. It supports deferred, restartable map exchange through XFS intent items; quota and extent-count accounting; reflink flag handling; post-operation conversion back to shortform for eligible attr/dir/symlink forks; and reservation/extent-count estimation before scheduling work.

## Intent and Fork Preconditions

`xfs_exchmaps_check_forks` rejects missing forks and local-format forks because local forks do not have bmbt mappings to exchange. The exchanged fork is selected from flags by `xfs_exchmaps_whichfork`.

`xfs_exchmaps_intent_init_cache` and `xfs_exchmaps_intent_destroy_cache` manage the slab cache for `struct xfs_exchmaps_intent`.

`xfs_exchmaps_init_intent` copies the request into an in-core intent, masks flags to allowed parameters, initializes sizes to `-1`, records size-swap targets when `XFS_EXCHMAPS_SET_SIZES` is present, sets internal post-op shortform flags for attr forks and for inode2 directories/symlinks, and decides whether reflink flags can be cleared/exchanged after a whole-file exchange.

## Mapping Discovery and Exchange

`xfs_exchmaps_find_mappings` walks both forks from the current intent offsets. It reads file1 mappings, optionally skips file1 unwritten/hole mappings under `XFS_EXCHMAPS_INO1_WRITTEN`, reads the corresponding file2 mapping, limits work to the smaller block count, and returns when the physical startblocks differ. Identical physical mappings with different states are treated as corruption and mark both bmaps sick.

Realtime files with multi-FSB allocation units have special skip trimming in `xfs_exchmaps_can_skip_mapping` so exchanges do not violate allocation-unit boundaries.

`xfs_exchmaps_one_step` updates quotas, unmaps both current records, swaps logical offsets, remaps each physical mapping into the other inode, updates on-disk sizes upward when needed to avoid post-EOF mappings during recovery, and advances the intent cursor.

`xfs_exchmaps_finish_one` is the deferred-operation worker:

- If mapping work remains, find and exchange one mapping step.
- If `XFS_EXCHMAPS_SET_SIZES` is requested and the range is complete, set both on-disk sizes.
- If mapping work is complete but post-op work remains, run post-op conversions/flag cleanup.
- Inject `XFS_ERRTAG_EXCHMAPS_FINISH_ONE` failures if configured.
- Return `-EAGAIN` to request another transaction while mapping or post-op work remains.
- At final completion, ensure CoW fork state and cowblocks tags are consistent for data-fork exchanges.

## Post-Operation Cleanup

`xfs_exchmaps_do_postop_work` performs internal cleanup flags:

- `__XFS_EXCHMAPS_INO2_SHORTFORM` may convert inode2's attr leaf back to shortform, directory block back to shortform, or remote symlink target back to local format if the data fits.
- `XFS_EXCHMAPS_CLEAR_INO1_REFLINK` and `XFS_EXCHMAPS_CLEAR_INO2_REFLINK` clear reflink flags after eligible full-file exchanges.

The shortform conversion helpers call existing attr, dir, and symlink code. Directory conversion uses `xfs_dir2_block_sfsize` and `xfs_dir2_block_to_sf` from this group.

## Estimation and Reservations

`xfs_exchmaps_estimate` simulates mapping exchange to fill:

- `ip1_bcount` / `ip2_bcount` or realtime block counters.
- `nr_exchanges`.
- Extent-count delta checks for both forks.
- Final reservation block estimate via `xfs_exchmaps_estimate_overhead`.

The estimator uses adjacent mapping records (`struct xfs_exchmaps_adjacent`) and merge predicates to estimate how removing the current mapping and adding the exchanged mapping changes extent counts. `xmi_delta_nextents_step` models whether current and replacement mappings are holes, merge with left/right neighbors, split existing mappings, or reduce counts by coalescing. `xmi_ensure_delta_nextents` checks overflow and large extent count limits, with `XFS_ERRTAG_REDUCE_MAX_IEXTENTS` available for fault testing.

`xfs_exchmaps_estimate_overhead` reserves potential bmbt and rmapbt growth for each side based on `nr_exchanges`, filesystem features, and realtime/data-device distinctions.

## Reflink and Extent Count Setup

`xfs_exchmaps_ensure_reflink` sets the reflink flag on the opposite inode before data-fork exchange when either inode already has shared blocks, ensuring later rmap/refcount operations use shared-block semantics.

`xfs_exchmaps_upgrade_extent_counts` sets `XFS_DIFLAG2_NREXT64` on both inodes when the filesystem supports large extent counts, avoiding per-inode narrow-counter limits during the exchange.

## Scheduling

`xfs_exchange_mappings` validates lock/flag assumptions, ignores zero-length requests, creates an intent, schedules it with `xfs_exchmaps_defer_add`, and performs pre-operation reflink/extent-count upgrades. The actual execution is done by deferred operations and can be recovered after crashes through the corresponding log item code outside this file.

## Dependencies and Interactions

This file integrates with bmap operations, quota accounting, deferred ops, exchange-mapping log items, tracepoints, error injection, attr/directory/symlink shortform conversion, reflink/COW fork state, and filesystem health marking. It is the main algorithmic implementation behind the public declarations in `xfs_exchmaps.h`.
