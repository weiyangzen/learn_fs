# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TupleTest.java

Purpose: small tuple smoke test with a legacy helper for incomplete versionstamp encoding behavior under older API versions.

Important APIs and flow: `incompleteVersionstamps300` verifies incomplete versionstamps do not compare equal to complete tuple values despite matching packed representations, checks encoded position suffixes, verifies subspace prefix position adjustment, and asserts oversized versionstamp offsets throw. `runTests` currently creates a tuple inside a transaction and prints timing data.

State and persistence: no intentional database writes. Dependencies are `FDB`, `Database`, `TransactionContext`, `Tuple`, `Subspace`, `Versionstamp`, `ByteBuffer`, and byte comparisons. Risks include the main path not invoking `incompleteVersionstamps300`, comments requiring API < 520 while `TestApiVersion.CURRENT` is higher, `System.exit`, and minimal active assertions. Signal is weak in current main flow, stronger if the legacy helper is explicitly invoked under a compatible API.
