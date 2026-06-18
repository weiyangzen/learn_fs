# sources/storage-engines/tikv/components/engine_traits/src/cf_options.rs

Purpose: Defines generic access to column-family options and Titan CF options.

Important APIs and control flow: `CfOptionsExt` associates an implementation-specific `CfOptions` type and exposes `get_options_cf` and `set_options_cf`. `CfOptions` provides getters/setters for write buffer count, L0 slowdown/stop triggers, compaction trigger, pending compaction limits, block cache capacity, Titan CF options, target file size, auto-compaction toggles, write-stall behavior, SST partitioner factory, and max compactions.

State, persistence, and dependencies: Implementations typically read/write live engine option state and may persist changes depending on backend behavior. It depends on `TitanCfOptions` and `SstPartitionerFactory`.

Integration points, risks, and test signals: Used by configuration reload, flow control, compaction scheduling, and cache resizing. Risks include string option names accepted by `set_options_cf`, backend-specific unsupported settings, lifetime of partitioner factories, and live mutation hazards. Signals are backend-specific option tests and runtime config update tests.
