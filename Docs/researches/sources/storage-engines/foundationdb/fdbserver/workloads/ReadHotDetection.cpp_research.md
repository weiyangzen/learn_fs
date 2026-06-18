## sources/storage-engines/foundationdb/fdbserver/workloads/ReadHotDetection.cpp

`ReadHotDetectionWorkload` creates a small keyset with one selected large hot key, drives read traffic toward that key, and checks whether `Database::getReadHotRanges` eventually reports a hot range containing it. It is a user-visible validation of read-hot metrics and storage metrics plumbing.

Important APIs are `ReadYourWritesTransaction`, `Database::getStorageMetrics`, `Database::getReadHotRanges`, `ReadHotRangeWithMetrics`, `DDSketch` include support, `poisson`, and random value generation. Options set duration, transactions per second, actors per client, and key count.

Setup writes `keyCount` keys named `testkey%08x`; the selected `readKey` always gets a 100 KB value and other keys get either large or small random values. `start` launches poisson-paced readers, with roughly 60% of actors reading the hot key and others reading random keys, and on client 0 starts `_check`. `_check` repeatedly retrieves storage metrics for the whole keyspace, calls `getReadHotRanges`, and sets `passed=true` once any returned range contains `readKey`; otherwise it sets `passed=false` and retries on transaction errors.

Persistent state is the test key range and large values. Runtime state includes reader futures, the checker future, `wholeRange`, and `passed`. A significant risk is that `passed` is not initialized in the constructor; if client 0 reaches `check` before `_check` sets it, result is undefined. The checker also uses `tr.onError(err)` even though its main calls are on `cx`, so invalid error handling paths should be reviewed.

Integration points are storage metrics, read-hot range detection, RYW read path, and workload traffic shaping. Test signals are `passed` on client 0 and trace comments left in the code for debugging; no metrics are exported.
