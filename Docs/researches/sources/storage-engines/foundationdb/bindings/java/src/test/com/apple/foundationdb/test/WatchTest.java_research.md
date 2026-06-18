# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/WatchTest.java

Purpose: manual watch API test covering cancellation and a repeated race between canceling and joining watch futures.

Important APIs and flow: `main` opens `args[0]`, sets a database option, starts a watch on key `a`, commits the transaction, cancels the watch, and expects cancellation error code 1101 when joining. `raceTest` creates a transaction and for 10,000 iterations watches key `hello`, then schedules cancel and join tasks in random order on a cached thread pool, waiting until both complete.

State and persistence: mostly read/watch state; it does not modify the watched key in this file. Dependencies include watch futures, `FDBException`, executor services, and transaction lifecycle. Risks include not shutting down the executor, verbose stderr/stdout, relying on watch cancellation code 1101, and using one transaction for many watch creations. Signal is absence of unexpected errors across race iterations.
