# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionPriority.java

Purpose: enum for level-compaction file picking priorities. Values include compensated size, oldest largest sequence, oldest smallest sequence, minimum overlapping ratio, and round-robin.

Control flow is Java-only enum mapping: each constant has a byte value, `getValue()` exposes it to option JNI callers, and `getCompactionPriority(byte)` scans values and throws for unknown bytes. State is immutable and not persisted by Java; the byte is persisted/consumed only through native option serialization or RocksDB configuration. Dependencies are minimal but semantic integration is with `ColumnFamilyOptions` compaction priority and C++ enum values.

Risks: byte values must match native RocksDB; adding a native priority without updating Java causes exceptions when reading options. Tests should assert all byte mappings, invalid-byte exceptions, and option round-trips through configuration parsing or JNI getters.
