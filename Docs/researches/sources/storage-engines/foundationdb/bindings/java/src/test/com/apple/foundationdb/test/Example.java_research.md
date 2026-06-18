# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Example.java

Purpose: minimal Java binding example demonstrating API version selection, database open, transaction retry wrapper, tuple key/value packing, and reading a value back.

Important APIs and flow: `main` selects `ApiVersion.LATEST`, opens the default database, runs one transaction that sets `Tuple.from("hello").pack()` to `Tuple.from("world").pack()`, then runs a read transaction and prints `Hello world`.

State and persistence: writes one user-space key named by the tuple encoding of `hello`. Dependencies are `FDB`, `Database`, and `Tuple`. Risks are limited but include mutating a shared cluster when run manually and using latest API rather than the repository's `TestApiVersion.CURRENT`. Test signal is the printed greeting and absence of exceptions.
