# Research: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_for_tiering_collector.h

- **Purpose:** Declares `CompactForTieringCollector`, a `TablePropertiesCollector` used to flag SST files for tiering-related compaction based on sequence-age eligibility.
- **Important APIs/types/functions:** Exports static property-name strings for eligible entries and data-age stats; constructor takes last-level sequence threshold, compaction trigger ratio, and age-stat flag. Overrides `AddUserKey`, `Finish`, `GetReadableProperties`, `Name`, and `NeedCompact`.
- **Control flow:** The header presents the collector lifecycle expected by RocksDB table building: create collector, call `AddUserKey` for every user entry, finalize with `Finish`, then query `NeedCompact`.
- **State and persistence behavior:** Private members hold threshold, ratio, counters, finish flag, compaction decision, and currently-unused data-age collection flag. Persisted output is via `UserCollectedProperties` populated in `Finish`.
- **Dependencies:** Depends only on `rocksdb/utilities/table_properties_collectors.h`, which provides the collector base class, entry types, sequence numbers, slices, status, and property maps.
- **Integration points:** Implemented in the matching `.cc` and instantiated by `CompactForTieringCollectorFactory` declared in the public utilities collector header. It plugs into SST table creation through RocksDB's table property collector interface.
- **Risks:** `Reset()` is private and only used internally; repeated reuse of collector instances would need careful lifecycle control. The header advertises data-age property names before the implementation supports them.
- **Test signals:** Header-level API expectations are exercised indirectly by tests that create collectors through the factory and call the virtual `TablePropertiesCollector` API.
