# sources/storage-engines/tikv/src/server/load_statistics/linux.rs

Purpose: Linux implementation of thread load statistics for selected TiKV threads, feeding shared `ThreadLoadPool` atomics that other code can use to detect heavy load.

Important APIs/types/functions: `ThreadLoadStatistics::new(slots, prefix, thread_loads)` discovers current process threads whose command starts with `prefix`; `record(instant)` samples `/proc/<pid>/task/<tid>` CPU counters; `calc_cpu_load` converts CPU counter deltas over elapsed milliseconds into a percentage-like integer.

Control flow: construction captures the process id, scans thread ids, filters by thread-name prefix, initializes an atomic load entry per matching tid, and seeds a ring buffer of CPU totals and instants. `record` writes the current slot, refreshes known tids, compares against the oldest slot in the ring, updates each thread's atomic load, and stores total load.

State and persistence: all state is in-memory. The object owns a fixed-size ring of historical CPU usage snapshots, a static tid list, and a shared `Arc<ThreadLoadPool>`. No persistent data is written.

Dependencies and integration: uses `tikv_util::sys::thread` for Linux `/proc` access and `ThreadLoadPool` from the sibling module. `raft_client` consumes the load pool indirectly to delay raft batch flushing under heavy send-thread load.

Risks: threads created after `new` are not discovered and exited/restarted tids are not refreshed. `thread_ids(pid).unwrap()` can panic if process thread enumeration fails. CPU load is clamped to 100 per thread, which hides oversubscription detail for individual threads but keeps threshold checks simple.

Test signals: `test_thread_load_statistic` starts a named busy-loop thread, records high load, then sleeps and verifies the load drops below threshold.
