# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_scan.c

## Role

Implements ZFS scrub, resilver, DDT scanning, sorted scan I/O queues, prefetch, async destroy/free processing, scan persistence, scan pause/resume/cancel, and hooks that keep scan state correct as datasets and vdev topology change.

## Scan Model

The file’s opening comment describes the modern sorted scan design:

- Metadata is traversed logically.
- Data I/O is queued by top-level vdev and sorted by physical LBA/extents.
- Memory use is bounded by hard/soft scan queue limits.
- Metadata traversal and queued I/O issuing are mutually exclusive in a txg.
- Periodic checkpoints persist restartable scan state.

Tunables control strict memory checks, inflight I/O, queue extent gaps, checkpoint interval, memory limits, scrub/resilver minimum txg time, disabling scrub I/O or prefetch, DDT class max, async free limits, and deferred resilver behavior.

## Core State and Data Structures

- `dsl_scan_phys_t` persists scan state in `DMU_POOL_SCAN`.
- `scan_ds_t` represents datasets queued for traversal.
- `scan_io_t` stores compact reconstructed block I/O metadata for sorted queues.
- `dsl_scan_io_queue_t` is per top-level vdev and owns:
  - address-sorted queued scan I/Os,
  - address and score-sorted extents,
  - memory usage,
  - inflight-byte limiting,
  - per-txg stats.
- `scan_prefetch_ctx_t` and `scan_prefetch_issue_ctx_t` support ordered metadata prefetch.

## Initialization and Persistence

- `scan_init()` creates `scan_io_t` slab caches and freezes the runtime fill-weight.
- `dsl_scan_init()` allocates scan state, loads old-style or current scan state, handles errata around historical overflow layout, reloads the dataset queue ZAP, detects restart conditions, and initializes scan stats.
- `dsl_scan_sync_state()` persists scan state only when sorted I/O queues are empty, unless writing a cached safe state after dataset mutation events.

## Starting, Canceling, Pausing

- `dsl_scan()` reopens vdevs, dispatches resilver restarts, resumes paused scrubs, or starts a new scrub via sync task.
- `dsl_scan_setup_sync()` initializes a scan, sets txg ranges, DDT class bounds, queue object, blkstats, scan events, labels, and history.
- `dsl_scan_cancel()` cancels a running scan.
- `dsl_scrub_set_pause_resume()` toggles paused scrub state and persists it with cached sync state.

## Traversal

Traversal proceeds through DDT, MOS, origin, datasets, snapshots, and clones:

- `dsl_scan_ddt()` walks dedup entries first to avoid repeated scrubbing of shared blocks.
- `dsl_scan_visit()` drives DDT, MOS, resume bookmark, and dataset queue traversal.
- `dsl_scan_visitds()` scans a dataset rootbp, handles ZIL for live heads, enqueues descendants and clones, and repeats a dataset if marked incomplete.
- `dsl_scan_recurse()`, `dsl_scan_visitdnode()`, and `dsl_scan_visitbp()` recursively read indirect blocks, dnodes, objsets, spill blocks, and accounting dnodes.
- Resume/suspend logic is bookmark-based and only resumes from safe level-0 points, while user/group/project accounting objects are never skipped.

## Prefetch

`dsl_scan_prefetch_thread()` consumes an AVL queue sorted in future traversal order. Prefetch reads metadata blocks with `ARC_FLAG_PRESCIENT_PREFETCH`, rate-limited by `spa_scrub_inflight`. Callback recursion schedules child metadata prefetches for indirect blocks, dnodes, and objsets.

## Sorted Scan I/O Queues

When not in legacy mode, `dsl_scan_enqueue()` creates per-top-level-vdev queues and inserts one `scan_io_t` per DVA unless the block is gang, in which case it is issued immediately.

Queue draining:

- `scan_io_queue_fetch_ext()` chooses the next extent: LBA order during checkpointing, largest/highest-score extent under memory pressure.
- `scan_io_queue_gather()` extracts up to 32 queued I/Os from an extent.
- `scan_io_queue_issue()` issues them and accounts pending bytes.
- `scan_io_queues_run()` dispatches one worker per top-level vdev.
- `ext_size_compare()` scores extents by fill bytes and fill ratio.

## Scrub and Resilver I/O

`dsl_scan_scrub_cb()` decides whether each block needs I/O:

- Scrub always needs I/O for in-range blocks.
- Resilver only issues I/O when DTL/vdev state says the DVA needs repair.
- ZIL blocks are speculative.
- Blocks outside the scan txg range are counted but not read.
- `scan_exec_io()` performs rate limiting, stats updates, ABD allocation, and async `zio_read()`.
- `dsl_scan_scrub_done()` frees ABD, reduces inflight counters, signals waiters, and increments scan errors except for speculative checksum failures.

## Async Destroy, Free, and Obsolete Processing

`dsl_scan_sync()` processes async destroys before scrub/resilver traversal so frees are handled before scanning. `dsl_process_async_destroys()` iterates `dp_free_bpobj`, async-destroy bptree, and obsolete bpobj, issuing frees or marking indirect mappings obsolete. It handles pause/restart by time, txg waiters, block count, shutdown, and recovery mode. It also transfers leaked free-dir accounting to `$LEAKED` when configured.

## Dataset Mutation Hooks

While a scan runs, dataset lifecycle changes rewrite cached/persistent scan state:

- `dsl_scan_ds_destroyed()` replaces or removes current/queued datasets.
- `dsl_scan_ds_snapshotted()` points traversal/queue state at the new snapshot.
- `dsl_scan_ds_clone_swapped()` swaps queued/current objset references during clone promotion.

These paths use `SYNC_CACHED` because sorted queues may contain pending I/O and the current live scan state may not be safe to persist.

## Freed-Block Queue Safety

`dsl_scan_freed()` is invoked during frees to remove corresponding cold queued scan I/Os from sorted queues. `dsl_scan_freed_dva()` finds the per-vdev queued DVA, removes it from `q_sios_by_addr`, adjusts extent fill, decrements pending bytes, and counts the block as examined. This prevents freed space from being reallocated while a stale scrub I/O remains queued.

## Vdev Interaction

- `dsl_scan_assess_vdev()` starts or restarts resilver based on DTL ranges.
- `dsl_scan_need_resilver()` checks indirect vdevs, gang blocks, partial DTL, offset need, and deferred resilver state.
- `dsl_scan_io_queue_vdev_xfer()` transfers a scan queue when top-level vdev structure changes during attach/detach.
