# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TestApiVersion.java

Purpose: single source for the API version used by standalone Java tests and benchmarks that are not part of normal CI.

Important APIs and flow: exposes `public static final int CURRENT = 800`. Comments note that these tests should be manually retested when the version changes.

State and persistence: no runtime state or persistence. Integration points are many manual test `main` methods that call `FDB.selectAPIVersion(TestApiVersion.CURRENT)`. Risks are version skew with generated bindings or cluster support; stale values can hide or create compatibility failures. Test signal is indirect because all dependent tests use this constant to select the binding API contract.
