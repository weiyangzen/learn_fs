# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ComparatorOptions.java

Purpose: native options controlling Java `AbstractComparator` callback buffering. APIs configure reused-buffer synchronization, whether direct byte buffers are used, and maximum reused buffer size.

Control flow asserts handle ownership before JNI get/set calls, then returns `this` for setters. State lives in a native comparator-options object and affects callback memory allocation/locking, especially the five retained comparator buffers described in comments. Dependencies include `RocksObject`, `AbstractComparator`, and `ReusedSynchronisationType`.

Risks: callers must dispose instances to release native memory; disabling direct buffers or changing reuse size changes callback allocation behavior and retained memory; assertions only run when enabled, so misuse may surface natively. Tests should round-trip all fields, verify invalid synchronization bytes through `ReusedSynchronisationType`, exercise Java comparator callbacks with reused buffers, and confirm disposal is safe.
