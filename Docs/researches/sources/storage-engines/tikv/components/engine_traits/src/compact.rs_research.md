# sources/storage-engines/tikv/components/engine_traits/src/compact.rs

Purpose: Defines generic manual compaction operations and compaction event metadata used by TiKV.

Important APIs and control flow: `ManualCompactionOptions` carries exclusivity, max subcompactions, bottommost-level force, and bottom-level range-overlap checking. `CompactExt` exposes auto-compaction status, range compaction across all CFs or one CF, file compaction by range or explicit file list, and range validation. `CompactedEvent` exposes compacted key ranges, byte-decline calculations, output level labels, and CF names.

State, persistence, and dependencies: Compaction rewrites persistent SST layout and may affect file sizes, snapshots, and range estimates. The trait depends on `CfNamesExt` and `BTreeMap` range accounting.

Integration points, risks, and test signals: Used by region split checks, manual admin compaction, GC, and size-decline heuristics. Risks include wrong range bounds, compaction stalls, file-level compaction with L0 exclusion, event byte attribution, and compaction during snapshots. Signals are backend compaction tests and split-check behavior; this file itself has no direct tests.
