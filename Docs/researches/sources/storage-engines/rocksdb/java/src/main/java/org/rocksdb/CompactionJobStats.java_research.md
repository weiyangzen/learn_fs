# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/CompactionJobStats.java

Purpose: JNI wrapper for detailed compaction counters and timings. APIs include `reset()`, `add()`, elapsed microseconds, input/output record and file counts, manual-compaction flag, byte totals, replacement/deletion/corruption counters, background IO nanosecond timings, output key prefixes, and experimental single-delete metrics.

Control flow delegates each operation to native methods using `nativeHandle_`. The public constructor allocates a stats object, while the package constructor wraps a native handle passed from `CompactionJobInfo.stats()`. The object has no Java-side persistence; it reflects native compaction statistics and can aggregate another native stats handle. Dependencies include `RocksObject`, `ColumnFamilyOptions.reportBgIoStats()` semantics, and the `Experimental` annotation.

Risks: `add()` assumes the other stats object is live, IO timing fields are only meaningful when background IO stats are enabled, experimental counters may change, and byte-array key prefixes depend on native copy semantics. Test signals should verify reset/add behavior, all JNI field mappings, optional population from compaction callbacks, and safe disposal after stats are returned from job info.
