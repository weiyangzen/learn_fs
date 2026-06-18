# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ParallelRandomScan.java

Purpose: range-read latency/throughput benchmark that launches random point-sized range scans at varying parallelism against a preloaded integer-key space.

Important APIs and flow: `main` opens `args[0]` and runs `runTest` for parallelism 10 through 100. `runTest` disables read-your-writes in a single transaction, obtains a read version once, then for a fixed duration uses a semaphore to cap outstanding async range reads. Each read chooses a random 4-byte key, calls `tr.getRange(key, Integer.MAX_VALUE, 1, false, StreamingMode.ITERATOR).iterator().onHasNext()`, records latency in `ContinuousSample`, and prints throughput and percentile stats.

State and persistence: read-only benchmark, but it assumes a database populated with integer keys, likely by `SerialInsertion`. Risks include using one long-lived transaction for all reads, semaphore coordination, approximate sampler correctness, and time-window races. Signal is stdout metrics and error counts.
