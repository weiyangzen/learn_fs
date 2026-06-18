# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/NativeComparatorWrapper.java research

## Purpose

`NativeComparatorWrapper` adapts a comparator implemented directly in C++ so it can be installed through Java APIs that expect an `AbstractComparator`.

## Important APIs and types

`getComparatorType()` returns `ComparatorType.JAVA_NATIVE_COMPARATOR_WRAPPER`. The Java comparator methods `name`, `compare`, `findShortestSeparator`, and `findShortSuccessor` are final and throw `IllegalStateException` because native code owns the implementation. `disposeInternal()` calls a native disposal function.

## Control flow

Subclasses or JNI create a wrapper around a native comparator handle. `Options.setComparator(AbstractComparator)` passes that handle and comparator type to native options. Any accidental Java-side comparator invocation fails loudly.

## State and persistence behavior

State is the native comparator handle inherited from callback/reference machinery. Comparator choice affects key ordering and therefore persistent SST and WAL interpretation; DBs must be reopened with a compatible comparator.

## Dependencies and integration points

It depends on `AbstractComparator`, `ComparatorType`, `ByteBuffer`, and options comparator installation. It is specifically for native comparators extending `rocksdb::Comparator`.

## Risks and test signals

The class prevents Java fallback, so wrong dispatch will fail at runtime. Lifecycle is delicate because the object is not a normal Java callback despite extending callback infrastructure. Tests should install a native comparator, verify ordering through writes/iterators, assert Java method calls throw, and verify disposal does not double-free.
