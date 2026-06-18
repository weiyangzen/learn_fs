# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/IterableTest.java

Purpose: small manual test for iterating a range with Java's enhanced-for syntax over `AsyncIterable<KeyValue>` inside `TransactionContext.run`.

Important APIs and flow: `main` selects `TestApiVersion.CURRENT`, opens the default database, and calls `runTests`. The test transaction iterates `tr.getRange("vcount", "zz")`, printing each key/value. It then prints timing counters and exits.

State and persistence: read-only over the specified key range; no writes. Dependencies are `FDB`, `Database`, `TransactionContext`, and `KeyValue`. Risks include `System.exit`, unused `reps`/`lastcount`, lack of assertions, and reliance on existing database contents. Signal is only stdout and exception absence.
