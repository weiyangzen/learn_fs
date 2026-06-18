# sources/storage-engines/tikv/components/engine_traits/src/range_properties.rs

Purpose: Declares the generic range-estimation APIs engines provide for split checks and size/key accounting.

Important APIs and control flow: `RangePropertiesExt` exposes approximate keys and size over all relevant CFs or one CF, plus approximate split-key selection over all CFs or one CF. `large_threshold` is explicitly for logging large ranges.

State, persistence, and dependencies: Implementations usually combine live memtable stats with persisted SST user properties. The trait depends on `Range` and common `Result`.

Integration points, risks, and test signals: Used by region split, scheduler, and diagnostics. Risks include approximation error, missing property collectors on older SSTs, CF aggregation choices, and split-key sampling quality. TiRocks range tests exercise property math and fallback; broader split tests validate operational behavior.
