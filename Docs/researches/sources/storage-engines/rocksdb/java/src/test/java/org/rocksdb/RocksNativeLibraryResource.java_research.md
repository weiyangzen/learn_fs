# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/RocksNativeLibraryResource.java

## Purpose

This small JUnit utility centralizes RocksDB JNI library loading for Java tests. It lets suites declare a `@ClassRule` so the native library is loaded before test methods run.

## Important APIs and types

The class extends `org.junit.rules.ExternalResource` and overrides `before()`. The only RocksDB API used is `RocksDB.loadLibrary()`.

## Control flow

JUnit invokes `before()` when the class rule is evaluated. The method delegates directly to `RocksDB.loadLibrary()` and performs no teardown.

## State and persistence behavior

The state is process-global native library loading. There is no database persistence and no instance-owned native handle.

## Dependencies and integration points

It integrates JUnit lifecycle with RocksDB JNI initialization and is referenced by many test classes in this package.

## Risks and test signals

Risks are limited to ordering: tests that need native symbols fail if this resource is absent or not class-scoped. The signal is indirect: all JNI-backed tests using the rule can construct native objects without explicit `@BeforeClass` calls.
