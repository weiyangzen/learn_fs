# sources/storage-engines/rocksdb/include/rocksdb/utilities/sim_cache.h

## Purpose
Simulated cache wrapper for estimating block-cache hit rates at alternate capacities without allocating the full simulated cache memory.

## Important APIs, Types, And Functions
`NewSimCache` constructs wrappers. `SimCache` extends `CacheWrapper` with simulated capacity/usage, hit/miss counters, counter reset, `ToString`, activity logging start/stop, and logging status.

## Control Flow, State, And Persistence
The wrapper forwards real cache behavior while maintaining simulated entries and counters. Capacity can be changed dynamically, evicting simulated entries on shrink. Activity logging writes cache activity to a file through an `Env` when enabled.

## Dependencies And Integration Points
Depends on `advanced_cache.h`, `CacheWrapper`, `Env`, `Statistics`, `Slice`, and `Status`. Integrates with cache tuning and instrumentation.

## Risks And Edge Cases
Pinned usage always reports zero, so behavior differs from a real cache. Simulated capacity is not actual memory usage. Logging can fail in the background and must be checked. Shrink behavior must purge correctly.

## Test Signals
Cover hit/miss counts, capacity changes, eviction, wrapped cache forwarding, stats strings, activity log limits/status, and shard-bit configurations.
