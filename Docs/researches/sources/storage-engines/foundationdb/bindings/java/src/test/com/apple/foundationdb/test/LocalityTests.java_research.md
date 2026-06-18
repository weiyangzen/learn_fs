# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/LocalityTests.java

Purpose: manual smoke test for Java locality APIs: storage server addresses for a key and boundary key iteration.

Important APIs and flow: `main` opens the cluster file from `args[0]`, calls `LocalityUtil.getAddressesForKey` for key `a`, then uses `LocalityUtil.getBoundaryKeys(database, begin, end)` over the user-space range. `AsyncUtil.collectRemaining` collects boundary keys from a `CloseableAsyncIterator`, which is closed by try-with-resources.

State and persistence: read-only metadata/locality access; no user data writes. Dependencies include locality APIs, async iterator collection, and printable byte utility. Risks include requiring a running cluster, system-key/locality permissions varying by configuration, potentially large boundary key output, and no assertions beyond exceptions. Signal is elapsed time, boundary count, printed addresses, and iterator closure behavior.
