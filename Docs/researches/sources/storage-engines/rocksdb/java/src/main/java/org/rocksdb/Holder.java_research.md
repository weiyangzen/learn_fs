# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Holder.java

Purpose: simple generic mutable reference wrapper for APIs needing an output parameter or mutable capture.

Control flow is pure Java: optional-value constructor, default null constructor, `getValue()`, and `setValue()`. State is one nullable reference; there is no synchronization, native handle, or persistence behavior. Dependencies are none beyond Java generics.

Risks: not thread-safe, nullability is only expressed in comments, and mutable holders can obscure ownership/lifetime of stored RocksDB objects. Tests are minimal: constructor/get/set behavior, null handling, and any API using `Holder` as an out parameter.
