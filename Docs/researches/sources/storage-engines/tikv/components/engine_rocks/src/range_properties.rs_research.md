<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/range_properties.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/range_properties.rs

Purpose: implements high-level range size/key estimation and split-key selection for `RocksEngine`.

Important APIs/types/functions: `RangePropertiesExt for RocksEngine`, including approximate keys, approximate size, per-CF variants, and split-key selection.

Control flow: key estimates prefer write-CF range properties and fall back to MVCC range stats. Size estimates sum large CFs and tolerate missing lock-CF range properties for old versions. Split-key selection chooses the largest CF by approximate size, gathers internal range-property sample keys, downsamples large sets, sorts, and picks evenly spaced keys.

State and persistence behavior: read-only aggregation of memtable stats and SST user properties; no DB mutation.

Dependencies/integration: depends on `MiscExt` property access, `RangeProperties::decode`, `get_range_stats`, TiKV CF constants, and logging wrappers.

Risks: estimates are approximate and can be wrong with stale or missing table properties. Large-threshold logging decodes properties with `unwrap`, assuming prior decode success. Sampling can miss ideal split points.

Test signals: property decoding and split source data are tested in `properties.rs`; this file has no direct tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/range_properties.rs -->
