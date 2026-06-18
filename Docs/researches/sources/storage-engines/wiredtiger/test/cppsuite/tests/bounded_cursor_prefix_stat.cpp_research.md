# sources/storage-engines/wiredtiger/test/cppsuite/tests/bounded_cursor_prefix_stat.cpp

## Purpose
Verifies that prefix-bounded `search_near` limits tree traversal by checking WiredTiger cursor statistics after controlled invisible-data searches.

## Important APIs, Types, And Functions
`class bounded_cursor_prefix_stat : public test` overrides `populate` and `read_operation`. Static helpers are `populate_worker` and `perform_search_near`. State includes `keys_per_prefix`, `srchkey_len`, alphabet constants, prefix length, and minimum expected entries.

## Control Flow
Population creates collections, starts 26 workers, and each worker inserts keys for one first-letter prefix across all two-letter suffixes, committing at timestamp 100. It then force-evicts pages via `debug=(release_evict=true)` and chooses a random search prefix length. Read operation asserts a single read thread, opens a connection statistics cursor, spawns configured `search_near_threads`, and each search worker performs a bounded search at read timestamp 10 where no populated keys are visible. After joining, it compares statistic deltas against expected skipped-entry upper bounds and early-exit counts.

## State And Persistence Behavior
Populated data is committed at timestamp 100 so read timestamp 10 sees none of it. The test uses statistics as its primary validation state and does not rely on value-level validation. Worker objects are allocated per spawned search thread and deleted after join.

## Dependencies And Integration Points
Depends on `bound_set`, constants/logger/random generator, base test, metrics monitor stats, timestamp manager, and `thread_manager`.

## Risks And Test Signals
The `z`, `zz`, `zzz` edge case is tracked because those prefixes can run to the end of the keyspace without early exit. Expected-entry math depends on `keys_per_prefix`, alphabet size, and prefix length. Success requires bounded early-exit stats to increase by thread count minus z-key searches and skipped entries to stay under the calculated upper limit.
