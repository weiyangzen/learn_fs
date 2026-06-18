# Research: sources/storage-engines/rocksdb/utilities/table_properties_collectors/compact_on_deletion_collector.h

- **Purpose:** Declares `CompactOnDeletionCollector`, a `TablePropertiesCollector` that observes delete density while an SST is built and reports whether the file should be compacted again.
- **Important APIs/types/functions:** Constructor takes `sliding_window_size`, `deletion_trigger`, `deletion_ratio`, and `min_file_size`. Overrides `AddUserKey`, `Finish`, `GetReadableProperties`, `Name`, and `NeedCompact`. `kNumBuckets` fixes the sliding window ring buffer at 128 buckets.
- **Control flow:** RocksDB calls `AddUserKey` for each emitted table entry and `Finish` when table properties are finalized. `NeedCompact` exposes the result to compaction scheduling.
- **State and persistence behavior:** The header lays out the complete in-memory state: deletion-count bucket array, current bucket counters, trigger/ratio configuration, total/delete entry counters, file-size threshold state, maximum observed window deletions, final compaction flag, and finish marker. It has no durable property output.
- **Dependencies:** Depends on the RocksDB table property collector interface and its entry-type/sequence/slice types.
- **Integration points:** Implemented and registered in the `.cc`; constructed by `CompactOnDeletionCollectorFactory` from public collector utilities APIs.
- **Risks:** `Reset()` is declared private but not implemented/used in the visible implementation, so reuse is not currently part of the lifecycle. The field `min_file_size_` is declared `size_t` while constructor accepts `uint64_t`, which can truncate on platforms where `size_t` is narrower.
- **Test signals:** API behavior is indirectly exercised by deletion-ratio, sliding-window, and minimum-size tests.
