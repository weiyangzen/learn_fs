# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionStyle.java

Purpose: enum selecting RocksDB compaction strategy: level, universal, FIFO, or none. It is used by column-family/options APIs to encode native compaction style.

Control flow is immutable enum byte exposure through `getValue()`. Unlike several other enums, this file has no reverse lookup method, so reverse conversion is handled elsewhere if needed. State is not Java-persisted; it affects native DB behavior through option setters and option files.

Risks: byte constants must match native order, and lack of local reverse lookup means callers may need separate conversion logic. Tests should assert byte values against JNI option round-trips and cover each compaction style’s interaction with its dedicated option class (`CompactionOptionsFIFO`, `CompactionOptionsUniversal`).
