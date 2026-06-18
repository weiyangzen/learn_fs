<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_scale_pool.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_scale_pool.rs

## Purpose
This file tests runtime resizing of raftstore execution resources: store/apply batch pools, raftstore-v2 pools, store IO pool, RocksDB high-priority background threads, and snapshot generator pool size.

## Important APIs, Types, and Functions
Tests use config controllers from simulators via `get_cfg_controller`, update keys such as `raftstore.store-pool-size`, `raftstore.apply-pool-size`, `raftstore.store-io-pool-size`, and `raftstore.snap-generator-pool-size`, and inspect current configs. Thread helpers `get_poller_thread_ids`, `get_raft_poller_thread_ids`, and `get_async_writers_tids` read OS thread names using `tikv_util::sys::thread`.

Failpoints include `poll`, `before_handle_tasks`, `on_flush_completed`, and `before_region_gen_snap`. The file also uses `ConfigurableDb::set_high_priority_background_threads`, engine `flush_cf`, and snapshot filters.

## Control Flow and Behavior
Pool-increase tests pause all existing pollers, show writes time out, increase pool size, and verify writes succeed. Decrease tests record thread IDs before and after shrinking and verify expected threads are removed while remaining threads are from the original set. v2 variants separately test store and apply pool resizing.

Store IO tests verify increasing async writers creates more writer threads, decreasing does not release existing writer threads, and switching between sync/async IO modes is rejected. High-priority RocksDB thread tests pause flush completion, reduce flush threads so flush blocks, then increase threads and unblock. Snapshot generator tests resize generation pools while snapshot generation is paused and verify only expected snapshots can proceed.

## State and Persistence
The file observes runtime config state, OS thread counts, key writes on engines, RocksDB flush progress, and snapshot delivery to lagging stores. It is mostly runtime behavior, but data writes verify resized pools still process persisted KV operations.

## Dependencies and Integration Points
It integrates raftstore batch systems, raftstore-v2 thread naming, YATP/snapshot generation, RocksDB thread configuration, failpoints, simulator config controllers, and engine reads.

## Risks
Risks include runtime config updates not taking effect, shrinking killing the wrong poller threads, writes remaining blocked after scaling up, invalid IO mode transitions being accepted, snapshot generation pool allowing unsafe zero size, and background flush thread changes not unblocking stalled flushes.

## Test Signals
Signals are write timeout vs success, current config values, thread ID count differences, preserved thread IDs after shrink, error results for invalid resize, blocked/unblocked flush channels, and expected key visibility or absence on lagging engines.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_scale_pool.rs -->
