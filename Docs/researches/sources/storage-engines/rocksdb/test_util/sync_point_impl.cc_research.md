# sources/storage-engines/rocksdb/test_util/sync_point_impl.cc

Purpose: implements debug-only kill-point random crashes and the core sync-point dependency engine.

Important APIs/control flow: `KillPoint::TestKillRandom()` returns if odds are disabled or the point has an excluded prefix, adjusts odds divisible by seven to avoid weak random coverage, then calls `port::Crash()` with source location when selected. `SyncPoint::Data::LoadDependency()` and `LoadDependencyAndMarkers()` rebuild predecessor/successor maps, marker maps, cleared trace, and bloom filter entries. `Process()` quickly skips disabled or unregistered points, records marker thread IDs, waits until all predecessors are cleared, runs callbacks outside the mutex, records the point as cleared, and notifies waiters.

State behavior: guarded maps track dependencies, callbacks, markers, marked thread IDs, and cleared points. `num_callbacks_running_` prevents callback clearing while callbacks execute. No durable state exists.

Dependencies/integration: uses TLS `Random`, `port::Crash`, condition variables, and `DynamicBloom` from the implementation struct. Called only through `SyncPoint` wrappers/macros.

Risks and test signals: dependency cycles can deadlock until processing is disabled. Callbacks run without the mutex, so they can race with test teardown unless cleared carefully. Tests should cover predecessor ordering, disable wakeups, marker same-thread filtering, callback clear waiting, and kill exclusion prefixes.
