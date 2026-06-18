# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialIteration.java

Purpose: scan throughput benchmark for iterating a large contiguous key range with configurable thread count.

Important APIs and flow: `main` opens a supplied cluster file and runs `runThreadedTest`. Each `IterationThread` performs `RUNS` scans with a randomized start delay, discarding the first run from averages. `scanDatabase` creates a transaction, disables read-your-writes, reads from empty key to `Integer.MAX_VALUE` with unlimited row limit and `StreamingMode.WANT_ALL`, and counts rows through a for-each iterator.

State and persistence: read-only, but assumes prior data loading, commonly by `SerialInsertion`. Risks include one transaction per full scan, unlimited row reads, no timeout/retry, hard-coded `THREAD_COUNT = 1`, and exception swallowing inside scan iteration. Signal is rows/sec printed per thread group.
