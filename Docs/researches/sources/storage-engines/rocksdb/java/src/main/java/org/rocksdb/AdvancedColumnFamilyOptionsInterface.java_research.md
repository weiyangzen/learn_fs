# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AdvancedColumnFamilyOptionsInterface.java

- **Purpose:** Contract for advanced non-mutable column-family options that complement the mutable options interface and are implemented by `ColumnFamilyOptions`.
- **Important APIs/types/functions:** Declares setters/getters for memtable merge thresholds, inplace updates, bloom locality, compression per level, level count, dynamic level bytes, max compaction bytes, compaction style/priority/options, optimize-filters-for-hits, and force consistency checks.
- **Control flow:** This interface has no implementation. It defines fluent setter return types through generic `T extends AdvancedColumnFamilyOptionsInterface<T> & ColumnFamilyOptionsInterface<T>`.
- **State and persistence behavior:** Implementations persist settings into native `rocksdb::ColumnFamilyOptions`; the options affect LSM layout, compaction behavior, filter memory use, consistency checks, and future SST generation.
- **Dependencies:** References `CompressionType`, `CompactionStyle`, `CompactionPriority`, `CompactionOptionsUniversal`, `CompactionOptionsFIFO`, `ColumnFamilyOptionsInterface`, and `@Experimental`.
- **Integration points:** Part of the public Java API for database/column-family creation and tuning, especially options not dynamically mutable after open.
- **Risks:** Many options materially affect storage layout and performance; dynamic-level bytes is marked experimental and can cause unexpected existing-DB LSM structure changes. Implementations must keep enum mappings and C++ option availability synchronized.
- **Test signals:** API compatibility tests, implementation coverage in `ColumnFamilyOptions`, native option round-trips, and integration tests opening databases with level/universal/FIFO compaction configurations.
