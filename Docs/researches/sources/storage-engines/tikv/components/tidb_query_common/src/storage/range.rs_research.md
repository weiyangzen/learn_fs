# sources/storage-engines/tikv/components/tidb_query_common/src/storage/range.rs

Purpose: represents point and interval key ranges for the legacy DAG scan path.

Important APIs and control flow: `Range` wraps either `PointRange` or `IntervalRange`. `Range::from_pb_range` turns a protobuf `KeyRange` into a point range when point ranges are accepted and `crate::util::is_point` says the start/end describe one key; otherwise it creates a lower-inclusive/upper-exclusive interval. Debug impls print keys through `log_wrappers::Value::key`. Conversions from byte vectors, strings, and string slices simplify tests and callers.

State and persistence behavior: value types own their key bytes. There is no persistence or cursor state.

Dependencies and integration: used by `RangesIterator` and `RangesScanner`, and by storage implementations receiving scan requests.

Risks and test signals: comments mark this module for removal after DAG v2. String/slice conversions are labeled "Maybe abuse" and are best suited to tests or simple call sites. Point detection depends on external `util::is_point`.
