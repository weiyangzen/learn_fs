## sources/storage-engines/foundationdb/fdbserver/workloads/RYWPerformance.cpp

`RYWPerformanceWorkload` is a microbenchmark for `ReadYourWritesTransaction` cache behavior. It loads `nodes` keys with `"bar"`, then prints operations/sec for repeated gets, sequential gets, range reads, and interleaved set/get patterns after filling the RYW cache in fourteen different ways.

Important APIs are `ReadYourWritesTransaction`, single-key `get`, `getRange`, `set`, `clear`, range clear, `waitForAll`, and the same monotonic `keyForIndex` style used by other tester workloads. `fillCache(type)` is the core matrix: pure sets, parallel gets, get-then-set combinations, full range reads followed by sets/clears, and many overlapping range reads followed by mutations.

Setup runs on client 0 and writes the baseline keys in one transaction. `_start` then serially executes `test_get_single` for cache types 0-13, `test_get_many_sequential` for 0-13, `test_get_range_basic` for 4-13, and `test_interleaved_sets_gets` for 0-13. Each test creates a RYW transaction, fills its cache, times the repeated operation loop with `timer()`, prints a throughput value to stderr, and returns without committing.

Persistent state is only the setup keyspace. The benchmark mutates local RYW state heavily but does not commit benchmark changes. Risks include printing rather than exporting structured metrics, very large `nodes` causing huge in-memory future vectors, no validation of results, and retrying an entire cache fill on error without resetting all local timing context. Because `check` returns true and metrics are empty, this file is useful mainly for ad hoc performance output.

Integration points are RYW cache algorithms, key-range read merging, mutation overlay behavior, and tester setup. Test signals are stderr rows of throughput values and assertion failures only from lower-level APIs.
