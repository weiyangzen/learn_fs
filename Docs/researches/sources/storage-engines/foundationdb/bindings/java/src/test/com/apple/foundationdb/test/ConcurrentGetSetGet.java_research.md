# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ConcurrentGetSetGet.java

Purpose: simple async concurrency stress program that runs many get/set/get transactions to expose callback, retry, or semaphore-leak failures in `Database.runAsync`.

Important APIs and flow: `apply` uses a `Semaphore` to cap outstanding transactions at `CONCURRENCY`, creates random `test:<int>` keys with `SecureRandom`, and launches `db.runAsync` transactions that get the key, set it to `value`, then read it again. Atomic counters record attempts, completed second gets, and errors; a background status thread prints progress.

State and persistence: writes random user-space keys prefixed `test:` and leaves them unless external cleanup occurs. Integration points are `Database.runAsync`, transaction read-your-writes behavior, `FDB.DEFAULT_EXECUTOR`, and semaphore coordination. Risks include `System.exit`, one-shot status thread, random key accumulation, and possible deadlock if a failure path misses semaphore release. Signal is final throughput and counter consistency.
