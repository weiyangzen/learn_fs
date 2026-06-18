# File Research: sources/windows/reactos/drivers/filesystems/btrfs/flushthread.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-7495, source bytes 262113, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_btrfs_flushthread_c_1_1_7495_0ac7e38d3f25_research.md`
- chunk 2: lines 7496-7946, source bytes 12910, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_btrfs_flushthread_c_2_7496_7_d1a442ac08b6_research.md`

## Chunk Research

### Chunk 1: lines 1-7495

# Chunk Research: sources/windows/reactos/drivers/filesystems/btrfs/flushthread.c lines 1-7495

## Scope

This report covers `sources/windows/reactos/drivers/filesystems/btrfs/flushthread.c` lines 1-7495 for subset A (`Docs/research_subset_a.md`). The chunk spans most of the WinBtrfs/ReactOS Btrfs flush path: physical writes, TRIM batching, dirty btree COW extent allocation and refcount conversion, tree splitting/merging, tree and superblock serialization, changed extent/checksum/chunk usage flushing, FCB and file-reference metadata batching, chunk creation/deletion, RAID5/6 partial-stripe completion, subvolume/root-ref updates, disk-cache flushing, device stats, orphan cleanup, and the prologue of `do_write2()`. It stops at line 7495 inside debug timing setup for `do_write2()`.

## APIs And Control Flow

- Physical IO helpers build and submit IRPs directly: `write_data_phys()`, `write_completion()`, `ioctl_completion()`, `flush_disk_caches()`, and superblock write helpers.
- Free-space cleanup merges chunk `deleting` ranges back into free-space lists and optionally maps them into per-device TRIM ranges. RAID0/10 and duplicate-like profiles are handled; RAID5/6 TRIM mapping is left as a FIXME.
- Tree flushing is COW-based: `add_parents()`, `allocate_tree_extents()`, `update_tree_extents()`, `do_splits()`, `write_trees()`, and `write_superblocks()` mark dirty ancestors, allocate fresh metadata blocks, convert refs, rebalance trees, serialize nodes, write metadata, and then persist superblocks.
- Metadata extent allocation prefers the original writable non-reloc chunk, scans matching existing chunks, then allocates a new metadata/system chunk if needed.
- Shared-tree conversion updates tree/data refs and changed-extent tracking so later extent-tree flushing can reconcile old and new refs.
- `do_tree_writes()` coalesces adjacent tree buffers, calls `write_data()`, waits for stripe IO, logs device write errors, and flushes RAID56 partial stripes.
- `add_checksum_entry()` rewrites overlapping `EXTENT_CSUM` ranges by deleting old items, overlaying new checksums or holes in a bitmap, and reinserting capped runs.
- `flush_fcb()` handles ADS xattrs, deleted inodes, extent checksums, extent merge/rationalization, sparse holes, inode item updates, security/DOS/reparse/EA/compression/case-sensitive xattrs, arbitrary xattrs, and orphan marking.
- `flush_fileref()` translates file-reference create/delete/rename/type changes into batched `DIR_ITEM`, `DIR_INDEX`, `INODE_REF`, `ROOT_REF`, and `ROOT_BACKREF` updates.
- `create_chunk()` and `drop_chunk()` add/remove chunk-tree, extent-tree, dev-tree, bootstrap, device accounting, free-space cache, TRIM, and incompat-flag state.
- RAID56 helpers read or reconstruct missing stripe data, zero unallocated/deleting ranges, write data stripes, and compute/write parity.
- `test_not_full()` implements a metadata reserve check to avoid COW dead-end full-filesystem states.
- `check_for_orphans_root()` opens orphan items, excises extents for zero-link files, marks FCBs deleted/dirty, deletes orphan items, and rolls back extent changes on error.

## State And Dependencies

Key state includes `Vcb->superblock`, roots, chunks, devices, dirty FCBs/filerefs, system chunk bootstrap entries, dirty trees, changed extents, partial stripes, rollback lists, batch lists, and per-FCB inode/extent/xattr fields.

The chunk depends on Windows kernel IRP, MDL, event, resource, pool, ATA pass-through, DSM TRIM, and bitmap APIs. It also depends on Btrfs driver helpers for tree search/update, extent refcounts, rollback, free-space lists, chunk allocation/cache loading, physical RAID writes, FCB lifecycle, and checksum/parity functions.

## Risks And Invariants

- Metadata COW correctness depends on precise refcount/ref-type conversion, especially for shared backrefs and unique-tree detection.
- Space accounting spans chunks, block groups, roots, superblock bytes used, device bytes used, free-space caches, and rollback lists.
- Batch item ownership is delicate: buffers become owned by the batch on success and must be freed only on failed insertion.
- `flush_fcb()` rewrites extent metadata broadly; hole insertion and extent merging rely on exact sector alignment and no-holes semantics.
- RAID56 partial-stripe reconstruction can corrupt parity if bitmap runs, degraded reads, or zero-fill ranges are wrong.
- TRIM is best-effort and clears local lists even though per-device discard failures are not propagated in detail.
- Several delete/reinsert flows must avoid using invalidated `traverse_ptr` item memory after deletion.
- `drop_chunk()` frees chunks during list iteration, so saved next pointers and lock-release ordering are critical.

## Cross-Chunk References

- Lines after 7495 complete `do_write2()`, final flush transaction ordering, rollback, batch commit, superblock writes, cache flushing, readonly transition, `do_write()`, `do_flush()`, and `flush_thread()`.
- `commit_batch_list()` and `clear_batch_list()` are used here but defined elsewhere; they should be linked to `insert_tree_item_batch()` in the merged report.
- `write_data()` and stripe structures are used by `do_tree_writes()` but defined outside this range.
- `update_changed_extent_ref()` and `add_changed_extent_ref()` are central to extent accounting here but are defined outside this chunk.

### Chunk 2: lines 7496-7946

# Chunk Research: sources/windows/reactos/drivers/filesystems/btrfs/flushthread.c lines 7496-7946

## Scope

This report covers `sources/windows/reactos/drivers/filesystems/btrfs/flushthread.c` lines 7496-7946 for subset A (`Docs/research_subset_a.md`). The chunk begins inside `do_write2()` after its local batch list setup and covers the main Btrfs transaction flush pipeline: orphan pre-checks, dirty fileref and FCB flushing, dirty subvolume/root/drop-root handling, chunk and device-stat updates, tree extent allocation/splitting/cache convergence, tree/superblock writes, post-commit state cleanup, `do_write()` rollback wrapping, `do_flush()` locking, and the periodic kernel `flush_thread()` routine.

The immediately preceding lines define `do_write2()` and `check_for_orphans()`, so this chunk inherits the initialized `batchlist`, `rollback`, `cache_changed`, `no_cache`, and optional debug timing/loop counters from earlier in the same function.

## APIs And Entry Points

- `do_write2(device_extension *Vcb, PIRP Irp, LIST_ENTRY *rollback)` is the internal writeback implementation. In this range it batches and commits dirty metadata, drives tree consistency, writes trees and superblocks, then resets dirty state after success.
- `do_write(device_extension *Vcb, PIRP Irp)` is the public wrapper declared in `btrfs_drv.h`; it creates a rollback list, calls `do_write2()`, forces readonly mode and notifies the filesystem runtime on failure, or clears rollback records on success.
- `do_flush(device_extension *Vcb)` is the timer/manual flush helper. It takes `Vcb->tree_lock` exclusively, writes only when `Vcb->need_write` and not readonly, frees cached trees, logs failures, and releases the lock.
- `flush_thread(void *context)` is the `KSTART_ROUTINE` for the mount's periodic flush thread. It references the `DEVICE_OBJECT`, initializes and arms `Vcb->flush_thread_timer`, waits on it in a loop, skips flushes while the volume is locked, exits on unmount/removal, signals `flush_thread_finished`, and terminates the system thread.

## Control Flow

`do_write2()` first checks orphan state for dirty filerefs, then takes `dirty_filerefs_lock` exclusively and drains `Vcb->dirty_filerefs` by removing each `file_ref`, calling `flush_fileref()`, and releasing it with `free_fileref()`. It commits the resulting `batchlist` immediately via `commit_batch_list()`.

Dirty FCB processing is split into two passes under `dirty_fcbs_lock`. The first pass handles `fcb->deleted` entries before other files, matching the nearby comment about avoiding xattr-limit pressure and inode collisions. Each FCB is locked through `fcb->Header.Resource`, flushed with `flush_fcb(fcb, false, &batchlist, Irp)`, unlocked, then released with `free_fcb()`. The second pass flushes remaining dirty FCBs whose `subvol` is not `Vcb->root_root`. The root tree FCBs are deliberately left out here, then the batch is committed after the lock is dropped.

Dirty subvolumes are drained without taking `dirty_subvols_lock` because the caller is expected to hold `tree_lock` exclusively. Drop roots, chunks, and batched tree edits follow: `drop_roots()` is called if `Vcb->drop_roots` is non-empty, `update_chunks()` may add batched changes and rollback entries, and the batch is committed.

The function then forces root/extent metadata into the write set. If the root root tree is missing or not marked for write, it performs a minimal `find_item()` lookup with a zero key to materialize/locate the tree and sets `tree->write = true`. It always calls `add_root_item_to_cache(Vcb, BTRFS_ROOT_EXTENT, Irp)` so the extent tree root item is refreshed.

If filesystem or device statistics changed, the code walks `Vcb->devices`, flushes each changed device with `flush_changed_dev_stats()`, clears each `dev->stats_changed`, and finally clears `Vcb->stats_changed`.

The central convergence loop repeatedly calls `add_parents()`, `allocate_tree_extents()`, `do_splits()`, and `update_chunk_usage()`. It then either allocates legacy free-space cache entries through `allocate_cache()` or updates the free-space cache tree through `update_chunk_caches_tree()` depending on `BTRFS_COMPAT_RO_FLAGS_FREE_SPACE_CACHE`. `allocate_cache()` failure is downgraded to a warning: `no_cache` is set, `cache_changed` is cleared, and the write continues without cache generation support. The loop repeats while cache allocation changed the tree or `trees_consistent(Vcb)` remains false.

After convergence, `update_root_root()` finalizes root-root metadata, `write_trees()` persists dirty tree blocks, and `test_not_full()` validates that the resulting filesystem is not overfull. Under `DEBUG_PARANOID`, each in-memory tree's address is verified against the extent tree as either a `TYPE_METADATA_ITEM` or `TYPE_EXTENT_ITEM`.

The final write phase sets `superblock.cache_generation` to the current generation, optionally flushes disk caches unless `options.no_barrier` is set, and writes all superblocks via `write_superblocks()`. If the volume has a parent volume device extension, it updates every `volume_child->generation` under `pdode->child_lock` shared.

On successful completion, the code cleans free-space cache state, clears each chunk's `changed` and `space_changed` flags, increments `superblock.generation`, clears every tree's `write` flag, marks `Vcb->need_write = false`, and drains `drop_roots`. Dropped roots with no FCBs have their `load_tree_lock`, nonpaged allocation, and root allocation freed; roots still referenced by FCBs are marked `dropped`.

`do_write()` owns rollback finalization around this pipeline. Failure sets `Vcb->readonly = true`, raises `FSRTL_VOLUME_FORCED_CLOSED` on `Vcb->root_file`, and calls `do_rollback()`. Success calls `clear_rollback()`.

`do_flush()` serializes all of the above through `tree_lock`, then calls `free_trees()` whether or not a write was needed. `flush_thread()` drives `do_flush()` periodically using a relative due time derived from `options.flush_interval` seconds.

## State And Data Structures

- Dirty queues: `Vcb->dirty_filerefs`, `Vcb->dirty_fcbs`, and `Vcb->dirty_subvols` hold pending file reference, file control block, and subvolume/root metadata updates.
- Synchronization: `dirty_filerefs_lock`, `dirty_fcbs_lock`, per-FCB `Header.Resource`, global `tree_lock`, flush-thread `KTIMER`, flush completion `KEVENT`, and parent device `child_lock`.
- Batching and rollback: local `batchlist` accumulates btree edits for `commit_batch_list()`, while caller-owned `rollback` records revertible tree/chunk/cache operations used by `do_write()` on failure.
- Tree/root state: `root_root`, `extent_root`, `Vcb->trees`, each `tree->write`, root treeholder state, root item cache, and `Vcb->drop_roots`.
- Chunk/device state: `Vcb->chunks`, `chunk->changed`, `chunk->space_changed`, `Vcb->devices`, `dev->stats_changed`, `Vcb->stats_changed`, and volume-child generation mirrors.
- Superblock state: `superblock.generation`, `superblock.cache_generation`, `superblock.compat_ro_flags`, and mount options `no_barrier` and `flush_interval`.
- Mount/lifecycle flags: `need_write`, `readonly`, `locked`, `removing`, and `VPB_MOUNTED` decide whether flushing occurs, succeeds, or terminates.

## Dependencies

This chunk depends on Windows kernel APIs for resources, timers, object references, events, system-thread termination, and volume notifications: `ExAcquireResourceExclusiveLite()`, `ExAcquireResourceSharedLite()`, `ExReleaseResourceLite()`, `ExDeleteResourceLite()`, `ExFreePool()`, `KeQueryPerformanceCounter()`, `KeInitializeTimer()`, `KeSetTimer()`, `KeWaitForSingleObject()`, `KeCancelTimer()`, `KeSetEvent()`, `ObReferenceObject()`, `ObDereferenceObject()`, `PsTerminateSystemThread()`, and `FsRtlNotifyVolumeEvent()`.

Btrfs-local dependencies include `check_for_orphans()`, `flush_fileref()`, `free_fileref()`, `flush_fcb()`, `free_fcb()`, `flush_subvol()`, `drop_roots()`, `update_chunks()`, `commit_batch_list()`, `clear_batch_list()`, `find_item()`, `add_root_item_to_cache()`, `flush_changed_dev_stats()`, `add_parents()`, `allocate_tree_extents()`, `do_splits()`, `update_chunk_usage()`, `allocate_cache()`, `update_chunk_caches_tree()`, `trees_consistent()`, `update_root_root()`, `write_trees()`, `test_not_full()`, `flush_disk_caches()`, `write_superblocks()`, `clean_space_cache()`, `free_trees()`, `do_rollback()`, and `clear_rollback()`.

The write path assumes `commit_batch_list()` and several tree-mutating helpers are called with `tree_lock` held exclusively; this is provided by `do_flush()` and by other external callers of `do_write()`.

## Risks And Invariants

- `do_write2()` has many early `return Status` paths before the final `end:` label. Because rollback is owned by `do_write()`, those returns still rely on the wrapper for rollback, but local `batchlist` cleanup is inconsistent: one deleted-FCB failure path calls `clear_batch_list()`, while several later failures return or jump without explicit batch clearing in this chunk.
- Dirty list mutation is destructive. `dirty_filerefs` and `dirty_subvols` entries are removed before their downstream operations fully complete, so failure recovery depends on rollback and object reference/lifetime rules outside this chunk.
- The dirty FCB two-pass order is an invariant for deleted streams and inode collision avoidance. Reordering these passes could change xattr and inode-number behavior.
- `dirty_subvols` is processed without its dedicated lock; correctness depends on exclusive `tree_lock` truly excluding concurrent dirty-subvolume producers or making them use compatible locking.
- `allocate_cache()` failure intentionally does not abort the transaction. It changes the final `update_root_root()` behavior through `no_cache`, so free-space cache consistency depends on that later propagation.
- `trees_consistent(Vcb)` and `cache_changed` control a potentially expensive convergence loop. Bugs in split/allocation/cache dirtying can cause excessive looping or non-termination.
- The superblock is written after `write_trees()` and optional disk cache flush. `no_barrier` weakens ordering, so crash consistency depends on user-selected mount policy.
- `Vcb->superblock.generation` is incremented only after successful superblock writes and child-generation propagation uses the pre-increment generation. Cross-device consumers must interpret this ordering consistently.
- Failure from `do_write2()` permanently flips the mount to readonly and notifies forced close. That is a coarse but protective response to metadata write failures.
- `flush_thread()` uses a relative timer interval computed as `(uint64_t)flush_interval * -10000000`; registry code outside this chunk normalizes zero intervals, and overflow or unexpectedly large values would affect timer scheduling.
- The thread exits on unmounted VPB or `Vcb->removing`, but it skips writes while `Vcb->locked`; dirty state can remain until a later manual or periodic flush.

## Cross-Chunk References

- Lines immediately before this chunk define `check_for_orphans()` and `check_for_orphans_root()`, which explain why dirty filerefs can trigger orphan cleanup before normal fileref flushing.
- Earlier `flushthread.c` sections define the heavy helpers used here: superblock writing, root-root update, tree writing, free-space cache allocation/update, chunk update, drop-root handling, and device-stat flushing.
- `treefuncs.c` defines `commit_batch_list()`, `do_rollback()`, and `clear_rollback()`, which are central to the batching and rollback contract visible in this chunk.
- `btrfs.c` initializes dirty lists/resources, mount options, and `flush_thread_finished`, starts/stops the flush thread, and marks `need_write` from metadata-changing operations.
- `fsctl.c`, `balance.c`, `scrub.c`, `pnp.c`, and other callers invoke or condition behavior on `do_write()` / `need_write`, so the final per-file report should connect this chunk's periodic writeback semantics to explicit flush, dismount, balance, scrub, and PnP paths.
- This is the final chunk of `flushthread.c`; no later same-file code follows the flush-thread routine.
