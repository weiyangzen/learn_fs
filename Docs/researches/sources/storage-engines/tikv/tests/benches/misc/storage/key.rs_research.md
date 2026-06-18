# sources/storage-engines/tikv/tests/benches/misc/storage/key.rs

Purpose: benchmarks `txn_types::Key::gen_hash` for common TiDB row and index key encodings.

Important APIs and functions: `gen_rand_str` creates random bytes; `bench_row_key_gen_hash` builds a row key with `table::encode_row_key`; `bench_index_key_gen_hash` encodes a 64-byte datum and builds an index seek key with `table::encode_index_seek_key`.

Control flow: each benchmark creates one key once and repeatedly calls `gen_hash` under `test::black_box`.

State and persistence: no storage state.

Dependencies and integration: uses TiDB datatype codec modules, `EvalContext`, `Datum`, and `txn_types::Key`. It belongs to the misc storage benchmark module.

Risks and test signals: random input means exact hash cost may vary slightly by run, but key shape is stable. Signal is CPU cost regression for hash generation used by storage and lock-management paths.
