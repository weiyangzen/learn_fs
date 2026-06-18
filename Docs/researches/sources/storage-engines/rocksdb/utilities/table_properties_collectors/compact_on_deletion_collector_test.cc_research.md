# Research: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_on_deletion_collector_test.cc

- **Purpose:** Unit tests for tombstone-density compaction decisions in `CompactOnDeletionCollector`.
- **Important APIs/types/functions:** Uses `NewCompactOnDeletionCollectorFactory`, collector `AddUserKey`, `Finish`, `NeedCompact`, and entry types `kEntryDelete`, `kEntrySingleDelete`, and `kEntryPut`.
- **Control flow:** `DeletionRatio` checks invalid ratios disable ratio mode and valid ratios trigger only after `Finish`. `SlidingWindow` builds deterministic and randomized windows and verifies the approximation within bucket bias. `MinFileSize` checks both sliding-window and ratio triggers under file-size thresholds.
- **State and persistence behavior:** Tests focus on internal compaction state exposed by `NeedCompact()` rather than persisted properties. They simulate file size by passing `file_size` to `AddUserKey`.
- **Dependencies:** Depends on DB format entry types, table property collector interfaces, RocksDB random/test harness utilities, and stack trace setup.
- **Integration points:** Validates collector behavior expected by table-building and compaction scheduling for tombstone-heavy SSTs.
- **Risks:** Sliding-window tests tolerate bucket bias and therefore do not assert exact window behavior near thresholds. Tests do not cover delete-with-timestamp entries, option parsing, string factory loading, or `GetReadableProperties()`.
- **Test signals:** Provides broad threshold coverage, randomized window sizes/triggers, high-volume non-triggering sections, and explicit minimum-size boundary checks.
