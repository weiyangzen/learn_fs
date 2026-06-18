# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/mod.rs

Purpose: declares the compact-log-backup execution-hook modules and provides shared statistic aggregation for hook implementations.

Important APIs and types: exports `checkpoint`, `consistency`, `observability`, `save_meta`, and `skip_small_compaction`; re-exports `SstCompressionType`; defines `CollectStatistic` with `LoadStatistic`, `SubcompactStatistic`, `LoadMetaStatistic`, and `CollectSubcompactionStatistic` fields.

Control flow: `CollectStatistic` is mutated by hooks as execution emits events. `update_subcompaction` accumulates load and compaction statistics from a `SubcompactionResult`; `update_collect_compaction_stat` and `update_load_meta_stat` accumulate the streaming deltas passed through `SubcompactionStartCtx`.

State and persistence: this module has only in-memory counters. Persistence is handled by hooks such as `save_meta`; observability serializes or logs the aggregate stats.

Dependencies and integration: depends on `compaction::SubcompactionResult` and the `statistic` module. It is used by `Observability` for progress reporting and Prometheus observations, and by `SaveMeta` to embed run comments in final migration metadata.

Risks: fields are private to the module, so new hooks outside this module cannot reuse the aggregator unless the API is opened. Statistics are additive deltas; if a hook updates from the wrong event or receives non-delta values, final comments and logs can overcount.

Test signals: no direct tests in this file, but `execute/test.rs` exercises `SaveMeta` and `Observability` paths that depend on these aggregations.
