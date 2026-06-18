# sources/object-store/rustfs/crates/io-core/src/deadlock_detector.rs

Purpose: in-memory wait-for graph tracker for detecting potential lock deadlocks and long-held locks.

Important APIs/types: `LockType` classifies mutex/rwlock/semaphore locks. `LockInfo` tracks lock id, type, owner thread id, waiters, and acquisition time. `WaitGraphEdge` connects a waiting thread to the thread holding the desired lock. `DeadlockDetectorConfig` controls interval, hold-time warning threshold, and enablement. `DeadlockDetector` registers locks, records acquire/release/wait events, detects cycles, tracks request IDs, and exposes lock/request counts.

Control flow: registered locks receive monotonically increasing IDs under a mutex. `record_acquire` sets owner/acquisition time, removes that waiter from the lock, and removes the wait edge for that lock/thread. `record_wait` adds waiter IDs and, if there is a different owner, pushes a wait graph edge. `detect_deadlock` builds an adjacency map and uses DFS with visited and recursion-stack sets to return a cycle path. `check_long_held` scans registered held locks for durations over `max_hold_time`.

State and persistence: all state is process-local behind `std::sync::Mutex`: locks, graph edges, request map, and next id. It is diagnostic state only.

Dependencies and integration: pure std, re-exported from `lib.rs`, and used in the scheduler example. The caller must instrument real locks with IDs and thread IDs.

Risks: stale wait edges can remain if callers fail to record acquire/release/unregister, causing false positives. Duplicate wait edges are not deduplicated. Poisoned mutex handling is inconsistent: some methods ignore lock failures while `lock_count` recovers poison. No background interval runner exists despite `detection_interval`.

Test signals: tests cover lock registration, acquire/release, request tracking, no-deadlock path, and disabled detector. There is no direct positive cycle test in the unit tests, though the example exercises one.
