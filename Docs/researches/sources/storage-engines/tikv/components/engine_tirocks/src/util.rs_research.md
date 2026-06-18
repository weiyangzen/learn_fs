# sources/storage-engines/tikv/components/engine_tirocks/src/util.rs

Purpose: Provides TiRocks engine construction helpers, CF reconciliation, slice transforms, perf-level conversions, and CF handle lookup.

Important APIs and control flow: `new_engine` builds defaults with statistics; `new_engine_opt` validates Titan/non-Titan option consistency, requires default CF, creates missing DBs, lists existing CFs, loads latest options, preserves existing `level_compaction_dynamic_level_bytes`, opens with missing CF support when needed, and destroys discarded non-default CFs. `FixedSuffixSliceTransform`, `FixedPrefixSliceTransform`, and `NoopSliceTransform` implement TiRocks prefix extraction. `to_rocks_perf_level`, `to_engine_perf_level`, and `cf_handle` bridge engine traits to TiRocks.

State, persistence, and dependencies: This file mutates persistent DB directory and column-family metadata. It depends on TiRocks builders, Titan builders, loaded CF options, `Env`, `Statistics`, and local option wrappers.

Integration points, risks, and test signals: Used by tests and constructors to open TiRocks-backed `RocksEngine`. Risks include accidental CF drops when desired CF lists are wrong, dangerous dynamic-level-byte changes, default CF omission, Titan option mismatches, slice-transform panics if called outside domain, and path/CF race conditions during open. Tests cover CF diffs, creating/opening/reordering/dropping CFs, preserving data, and retaining dynamic-level-byte settings.
