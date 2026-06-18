<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/properties.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/properties.rs

Purpose: implements SST table-property formats and collectors for range size/key estimates, Titan blob size estimation, MVCC statistics, RawKV TTL stats, and range stats.

Important APIs/types/functions: `SizeProperties`, `UserProperties`, `UserCollectedPropertiesDecoder`, `RangeOffsets`, `RangeProperties`, `RangePropertiesCollector`, factories, `MvccPropertiesCollector`, raw/txn MVCC factories, `get_range_stats`, and Titan compression-factor globals.

Control flow: range collectors count entry sizes/keys and insert offset points after size/key distance thresholds. Titan blob indexes are decoded and adjusted by smoothed compression factor and max blob size. MVCC collectors validate data keys, split timestamps, count rows/versions/puts/deletes/stale versions, build row indexes, and encode final user properties.

State and persistence behavior: writes compact binary metadata into SST user properties; global atomics/smoother influence Titan size estimates. Query functions aggregate persisted table properties.

Dependencies/integration: consumed by split checking, GC/statistics, iterator table filters, and `range_properties.rs`.

Risks: corrupt keys/properties degrade to errors or counters; table-property approximations can drift, especially with Titan compression estimates. RawKV mode depends on API v2 value decoding.

Test signals: extensive tests cover range estimates, blob indexes, range stats, transactional MVCC, RawKV TTL/deletes, and blob entry size estimation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/properties.rs -->
