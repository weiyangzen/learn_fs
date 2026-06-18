# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionOptionsUniversal.java

Purpose: native option wrapper for universal compaction. APIs configure size ratio, minimum/maximum merge width, maximum size amplification, compression size percent, compaction stop style, and trivial-move allowance.

Control flow is fluent Java-to-JNI forwarding. `stopStyle()` maps the native byte through `CompactionStopStyle.getCompactionStopStyle`; `setStopStyle()` passes the enum byte to native options. State is not persisted by Java but becomes part of column-family options and influences universal compaction picking and output compression strategy. Dependencies include `RocksObject`, `CompactionStopStyle`, and the C++ universal compaction option layout.

Risks: the options have strong performance implications and defaults live natively; invalid values are not validated in Java, unknown stop-style bytes throw, and native enum drift would break mapping. Tests should round-trip each property, cover stop-style conversion, and use integration compaction tests to ensure merge width and amplification settings affect compaction scheduling as expected.
