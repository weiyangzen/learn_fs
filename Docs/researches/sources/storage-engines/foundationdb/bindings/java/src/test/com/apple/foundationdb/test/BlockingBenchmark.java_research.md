# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/BlockingBenchmark.java

Purpose: microbenchmark for Java future blocking overhead on a transaction with a fixed read version, intended to measure client-side future completion costs without depending on real database contact.

Important APIs and flow: `main` selects `TestApiVersion.CURRENT`, opens a database and transaction, sets the read version, then times several blocking strategies over `tr.getReadVersion()`: `join`, `get`, one async identity callback, ten chained async callbacks, and repeated `get`. `runTests` measures both serial and `PARALLEL` batched future blocking.

State and persistence: no intended database persistence; the transaction read version is set explicitly and only read-version futures are created. Dependencies are `FDB`, `Database`, `Transaction`, `CompletableFuture`, and `FDB.DEFAULT_EXECUTOR`. Risks include coarse millisecond timing, ignored exceptions, and reliance on an openable cluster file/database object even though reads should not contact storage. Test signal is performance-only stdout, not assertions.
