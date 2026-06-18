# sources/storage-engines/tikv/components/concurrency_manager/benches/lock_table.rs

Purpose: Criterion benchmark suite for point and range lock checks in `ConcurrencyManager` with 10,000 resident in-memory locks.

Important APIs and types: constants `KEY_LEN` and `LOCK_COUNT`, helper `prepare_cm`, and benchmark functions `point_check_baseline`, `bench_point_check`, `range_check_baseline`, and `bench_range_check`.

Control flow: `prepare_cm` creates random 64-byte keys, locks each key, stores a `Lock`, then leaks the guard with `forget` so the lock remains present. Point benchmarks compare random key construction baseline against `read_key_check` plus `txn_types::check_ts_conflict`. Range benchmarks compare random range key construction against `read_range_check` over a rough tenth of the one-byte key space.

State and persistence: in-memory only. Guards are intentionally leaked for benchmark setup, so this code is not a production pattern.

Dependencies and integration: exercises `ConcurrencyManager`, `txn_types::Lock`, `TsSet`, `IsolationLevel`, Criterion, random generation, and futures `block_on` for async lock acquisition.

Risks: random duplicate keys are ignored as “really rare”; actual lock count can be slightly below target. Leaking guards avoids teardown costs but can hide drop-time behavior. Range key distribution uses single-byte bounds, unlike real encoded TiKV keys.

Test signals: provides performance signals for lock table lookups and range scans, not correctness assertions.
