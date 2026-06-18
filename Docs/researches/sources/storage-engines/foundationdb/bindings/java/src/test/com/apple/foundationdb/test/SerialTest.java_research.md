# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialTest.java

Purpose: simple serial transaction throughput smoke test for repeated get/set increments of a `count` key.

Important APIs and flow: `runTests` loops `reps` times calling `db.run`; each transaction reads `count`, parses it as an integer, writes incremented text, and records the prior value. It prints total time and transactions per second, then exits.

State and persistence: mutates the user-space `count` key and requires it to already contain a parseable integer; no initialization is present. Dependencies are `FDB`, `Database`, `TransactionContext`, and retry wrappers. Risks include `NumberFormatException` on missing data, non-isolated key use, `System.exit`, and no assertions. Signal is throughput output and exception traces.
