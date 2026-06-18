# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_initialize.c

## Purpose
Implements vdev initialization, a best-effort background process that writes a known filler pattern to free regions of a leaf vdev. It persists progress and state in leaf ZAP entries so initialization can be suspended, canceled, completed, or resumed after import.

## Tunables And State
- `zfs_initialize_value` is the 64-bit pattern written to disk, defaulting to `0xdeadbeefdeadbeef`.
- `zfs_initialize_limit` caps outstanding initialization I/Os per leaf vdev.
- `zfs_initialize_chunk_size` controls physical write size, defaulting to 1 MiB.
- Persistent ZAP keys store initialize state, last offset, and action timestamp.

## Main Responsibilities
- Decide when initialization must stop: requested exit, non-writable vdev, detached vdev, or top-level removal.
- Persist state transitions and progress through sync tasks using vdev GUIDs rather than raw `vdev_t *` pointers, because a vdev can be freed before the sync task runs.
- Estimate progress from metaslab free space and the last initialized physical offset.
- Walk free metaslab ranges, translate logical ranges to leaf physical ranges, and write initialized chunks.
- Start, stop, wait for, restart, and recursively stop initialization threads.

## Key Functions
- `vdev_initialize_zap_update_sync()` resolves the vdev by GUID in syncing context and writes `INITIALIZE_LAST_OFFSET`, `INITIALIZE_ACTION_TIME`, and `INITIALIZE_STATE`.
- `vdev_initialize_change_state()` changes in-memory state, schedules the ZAP sync task, logs spa history, and wakes waiters for terminal/non-active states.
- `vdev_initialize_write()` throttles inflight I/O, obtains a txg, schedules a progress ZAP update for the txg, checks stop conditions under locks, records the offset for that txg, and issues `zio_write_phys()`.
- `vdev_initialize_calculate_progress()` sums free metaslab space, with RAID-Z adjustment by child count, and loads the current metaslab only when the saved offset lies inside it.
- `vdev_initialize_range_add()` translates logical free ranges to the leaf vdev, clips already-initialized portions, and adds nonempty physical ranges to the initialize range tree.
- `vdev_initialize_thread()` drives the process: load progress, allocate filler ABD, iterate metaslabs, disable/load each metaslab, collect free ranges, write them, re-enable/unload as appropriate, wait for inflight I/O, then mark complete if not stopped.
- `vdev_initialize_stop_all()` recursively requests a target state for all concrete leaves and waits for their threads before syncing state to disk.
- `vdev_initialize_restart()` reads persisted state and action time; suspended/offline devices only load reporting progress, while active writable devices resume.

## Important Behavior And Invariants
- Initialization is best-effort. Non-availability rolls back the recorded offset for the txg, but other I/O errors only increment `vs_initialize_errors`.
- Sync task data is a copied GUID, freed by the sync callback.
- The initialize thread drops locks around `txg_wait_synced()` to avoid deadlock with online/import paths holding config locks.
- RAID-Z leaves may receive no translated range for a logical free segment; zero-length physical ranges are ignored.

## Dependencies
Uses SPA config locking, ZIO physical writes, DMU transactions and sync tasks, metaslab loading/disabling, range trees, ABD buffers, vdev translation, and leaf/top ZAP metadata.
