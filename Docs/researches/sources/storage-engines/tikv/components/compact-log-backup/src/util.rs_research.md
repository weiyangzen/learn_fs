# sources/storage-engines/tikv/components/compact-log-backup/src/util.rs

Purpose: provides small shared helpers for cooperative async execution, unordered future selection, bounded concurrent execution, CF parsing, formatting, compression encoding, key redaction, end-key ordering, and storage URL rendering.

Important APIs and types: `Cooperate`, `Step`, `select_vec`, `ExecuteAllExt`, `execute_all_ext`, `cf_name`, `aligned_u64`, `compression_type_to_u8`, `redact`, `EndKey`, and `storage_url`.

Control flow: `Cooperate::step` returns a future that yields every configured number of operations. `select_vec` polls a vector of futures and `swap_remove`s the first ready future. `execute_all_ext` submits futures up to `max_concurrency` and gathers results with error propagation.

State and persistence: no persistence. `Cooperate` tracks only per-instance counters.

Dependencies and integration: used by source loading, execution task waiting, metadata prefix hashing, storage logging, and compaction logic that needs TiKV CF names or end-key ordering.

Risks: `select_vec` is intentionally unordered and mutates future vector order, so callers must not rely on stable completion ordering. `execute_all_ext` requires `Unpin` futures. `cf_name` maps unknown CF strings to `"ERR_CF"`, relying on downstream filtering rather than returning an error. `compression_type_to_u8` must stay in sync with `SstCompressionType` variants for stable prefix hashing.

Test signals: no direct tests here; behavior is indirectly exercised by execution scheduling, source event iteration, shard prefix generation, and compaction collection tests.
