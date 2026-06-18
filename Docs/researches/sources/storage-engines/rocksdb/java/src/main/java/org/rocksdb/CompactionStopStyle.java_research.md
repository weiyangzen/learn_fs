# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionStopStyle.java

Purpose: enum for universal compaction stop style. `CompactionStopStyleSimilarSize` stops when file sizes diverge, and `CompactionStopStyleTotalSize` uses total size criteria.

Control flow is byte mapping for JNI options: `getValue()` exposes the byte and `getCompactionStopStyle(byte)` scans/throws. State is immutable and consumed by `CompactionOptionsUniversal`. There is no persistence behavior in Java beyond native option serialization.

Risks: byte mapping must stay synced with native `CompactionStopStyle`; unknown native bytes throw when read from options. Tests should cover both values, invalid input, and round-trips through `CompactionOptionsUniversal.setStopStyle()`/`stopStyle()`.
