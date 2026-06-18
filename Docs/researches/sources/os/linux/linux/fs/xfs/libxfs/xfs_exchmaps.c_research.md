# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_exchmaps.c

## Purpose

Implements XFS deferred file mapping exchange operations for the exchange-range feature: request validation, mapping discovery, quota and bmap updates, crash-resumable finish steps, post-operation shortform/reflink cleanup, reservation/extent-count estimation, intent allocation, reflink/large-extent-count preparation, and scheduling of exchange intent work.

## Main Interfaces

- Validation and lifecycle: `xfs_exchmaps_check_forks()`, `xfs_exchmaps_intent_init_cache()`, `xfs_exchmaps_intent_destroy_cache()`, `xfs_exchmaps_init_intent()`.
- Deferred execution: `xfs_exchmaps_finish_one()`, `xfs_exchange_mappings()`.
- Estimation: `xfs_exchmaps_estimate()`, `xfs_exchmaps_estimate_overhead()`.
- Inode preparation: `xfs_exchmaps_ensure_reflink()`, `xfs_exchmaps_upgrade_extent_counts()`.
- Internal execution helpers: mapping lookup/skip logic, `xfs_exchmaps_one_step()`, post-op conversion helpers for attributes, directories, and symlinks.

## Control Flow And Behavior

Fork validation rejects missing forks and local-format forks because mapping exchange works on extent/btree mappings. Intent initialization copies inode pointers, start offsets, blockcount, and allowed flags into an in-core deferred intent. Attribute-fork exchanges always request inode2 shortform cleanup; data-fork exchanges can request size swapping, reflink flag cleanup, and shortform cleanup for inode2 directories or symlinks.

`xfs_exchmaps_find_mappings()` walks the two file ranges while both inodes are ILOCKed and page cache has been flushed by callers. It reads one mapping from inode1, optionally skips unwritten or hole mappings when `XFS_EXCHMAPS_INO1_WRITTEN` allows it, reads the corresponding inode2 mapping, trims to the smaller mapping length, and ignores identical physical mappings unless their states differ, which is treated as corruption. Realtime files with large allocation units get special skip/trim rules to avoid exchanging partial unwritten allocation units incorrectly.

`xfs_exchmaps_one_step()` accounts quota deltas, removes both mappings, swaps logical offsets, maps each physical extent into the opposite inode, updates on-disk sizes upward if needed to avoid post-EOF mappings during recovery, and advances the intent cursor. `xfs_exchmaps_finish_one()` performs one exchange step per transaction, swaps final file sizes when requested, runs post-operation cleanup when range exchange is done, injects `EXCHMAPS_FINISH_ONE` failures for testing, and returns `-EAGAIN` when the deferred item needs relogging for more work.

Post-operation cleanup can convert inode2 attr leaf format back to shortform, convert a block-format directory back to shortform, convert a remote symlink target back to local format, and clear reflink flags that are being effectively exchanged. Final completion ensures CoW forks and cowblocks tags match reflink state and CoW fork contents.

Estimation simulates mapping exchanges to count affected data or realtime blocks, number of exchange steps, possible extent-count growth, bmbt reservation overhead, and rmapbt overhead. It models how deleting the current mapping and adding the swapped mapping can merge with left/right neighbors, checks extent-count overflow, applies the error tag that reduces max extent counts, and updates reservation fields in the request.

`xfs_exchange_mappings()` asserts both inodes are exclusively ILOCKed and joined, rejects incompatible flags, creates an intent for nonzero ranges, attaches it to deferred operations, ensures reflink flags are set on both inodes if either side has shared blocks, and upgrades extent-count fields when the filesystem supports large counters.

## State And Data Structures

`struct xfs_exchmaps_intent` tracks the two inodes, current logical offsets, remaining block count, optional final file sizes, and flags. `struct xfs_exchmaps_adjacent` caches left/right bmbt records during estimation. Mapping changes operate on `struct xfs_bmbt_irec` records and are made persistent through deferred log intent/done items outside this file.

## Dependencies

Depends on bmap read/map/unmap helpers, deferred-operation infrastructure, quota accounting, rmap/bmbt transaction reservation formulas, reflink/CoW fork state, attr leaf-to-shortform conversion, directory block-to-shortform conversion, remote symlink read/truncate helpers, inode logging, tracepoints, health marking, and `xfs_errortag.h`.

## Risks And Invariants

- Callers must hold exclusive inode locks, flush delalloc/pagecache, and join inodes to the transaction before scheduling work.
- Mapping discovery assumes no delalloc mappings and exact start offsets; violations are treated as logic errors or invalid input.
- Exchange steps must not create post-EOF mappings visible to log recovery without first raising on-disk size.
- Reservation estimation must conservatively handle bmbt/rmapbt splits and extent counter growth.
- Reflink and CoW fork state must be repaired after data-fork exchanges so later shared-block and preallocation cleanup paths work.
