# sources/storage-engines/tikv/src/server/load_statistics/mod.rs

Purpose: provides the platform-neutral public surface for thread load tracking and exports the Linux implementation or a non-Linux no-op implementation.

Important APIs/types/functions: `ThreadLoadPool::with_threshold`, `current_thread_in_heavy_load`, and `total_load` are the main API. Thread-local `CURRENT_LOAD` caches the current thread's atomic load entry. `ThreadLoadStatistics` is re-exported from `linux` on Linux and from `other_os` elsewhere.

Control flow: `current_thread_in_heavy_load` lazily inserts or retrieves the current thread id in the shared `stats` map, then compares the atomic load against the configured threshold. `total_load` reads the aggregate atomic. Non-Linux `ThreadLoadStatistics` accepts calls but records nothing.

State and persistence: state is process-local: a mutex-protected map of thread ids to atomics, a threshold, an aggregate atomic, and thread-local cached handles. No persistence or network behavior exists.

Dependencies and integration: uses `parking_lot::Mutex`, TiKV thread id helpers, and is integrated by components that need adaptive behavior under CPU load, notably raft batching.

Risks: the current-thread cache can create entries that are never sampled by a `ThreadLoadStatistics` collector if the thread did not match the collector prefix. Relaxed atomics are appropriate for approximate metrics but should not be treated as synchronization. Non-Linux behavior silently reports no load.

Test signals: direct tests live in `linux.rs`; module-level behavior is covered through that implementation and downstream consumers.
