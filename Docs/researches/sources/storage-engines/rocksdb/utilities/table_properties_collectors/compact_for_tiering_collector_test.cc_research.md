# Research: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_for_tiering_collector_test.cc

- **Purpose:** Unit tests for the tiering collector factory and collector thresholds.
- **Important APIs/types/functions:** Uses `NewCompactForTieringCollectorFactory`, `TablePropertiesCollectorFactory::Context`, `AddUserKey`, `Finish`, `NeedCompact`, `PackValueAndSeqno`, and `kEntryTimedPut`.
- **Control flow:** Tests construct contexts representing enabled tiering, disabled tiering, and last-level file creation. Enabled tests add 100 entries, finish the collector, and check the eligible-entry property and compaction decision against ratio thresholds.
- **State and persistence behavior:** Verifies per-file collector counters and `NeedCompact()` state before and after `Finish()`. The test inspects emitted `UserCollectedProperties`, not persisted SST files.
- **Dependencies:** Depends on the collector header, sequence packing helper, table property types, RocksDB test harness, and stack trace setup.
- **Integration points:** Validates factory behavior for RocksDB table-builder contexts: no collector for disabled settings, a collector for non-last-level files with valid tiering threshold, and timed-put sequence extraction.
- **Risks:** Tests use simple numeric sequences and do not cover empty files, ratio > 1 after finish beyond non-trigger behavior, option-string parsing, or age-stat APIs that return `NotSupported`.
- **Test signals:** Strong signals are `NotEnabled`, `TieringDisabled`, `LastLevelFile`, `CollectorEnabled`, and `TimedPutEntries`.
