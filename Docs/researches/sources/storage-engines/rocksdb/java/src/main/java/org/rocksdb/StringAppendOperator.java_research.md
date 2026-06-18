# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StringAppendOperator.java

## Purpose
`StringAppendOperator` exposes RocksDB's built-in string-append merge operator to Java.

## Important APIs and Types
It extends `MergeOperator`. Constructors select a comma delimiter by default, a single `char` delimiter, or a `String` delimiter. Native allocation uses `newSharedStringAppendOperator`.

## Control Flow
Construction creates a shared native merge-operator handle. Disposal releases it through `disposeInternalJni`.

## State and Persistence Behavior
The Java object owns a native merge operator. Merge effects are persisted only when attached to options and used by database writes/compaction; the wrapper stores no values itself.

## Dependencies and Integration Points
It integrates with column-family/options merge-operator configuration and native merge implementation.

## Risks and Test Signals
Tests should verify delimiter overloads, UTF-16 to native string handling, lifecycle when attached to options, and merge results across put/merge/get/compaction. Native ownership semantics are the main integration risk.
