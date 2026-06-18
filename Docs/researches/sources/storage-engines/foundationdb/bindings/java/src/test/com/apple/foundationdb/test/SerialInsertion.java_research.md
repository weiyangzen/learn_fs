# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialInsertion.java

Purpose: data loader benchmark that inserts one million 4-byte integer keys from multiple threads in batched transactions.

Important APIs and flow: `main` starts `THREAD_COUNT` `InsertionThread`s, dividing key ranges among them. Each thread reuses a `ByteBuffer` for big-endian integer keys, stages up to `BATCH_SIZE` sets per transaction, commits, then creates a new transaction. Runtime exceptions are passed to `tr.onError(e).join()` for retry handling.

State and persistence: writes keys from `0` to `NODES - 1` with value `....` into user space and does not clear first. Dependencies are `FDB`, `Database`, `Transaction`, and Java threads. Risks include duplicate/incorrect ranges if node division changes, committing large batches near transaction limits, no cleanup, and broad `RuntimeException` retry handling. Signal is elapsed time and absence of uncaught thread failures.
