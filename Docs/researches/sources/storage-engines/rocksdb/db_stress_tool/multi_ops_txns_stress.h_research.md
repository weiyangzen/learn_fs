# sources/storage-engines/rocksdb/db_stress_tool/multi_ops_txns_stress.h

## Purpose
`multi_ops_txns_stress.h` declares the multi-operation transaction stress workload. The header documents the table model, key/value encodings, and transaction scenarios used to validate TransactionDB consistency through paired primary and secondary indexes.

## Important APIs, types, and functions
The central type is `MultiOpsTxnsStressTest : public StressTest`. Nested `Record` owns encoding/decoding for primary keys, primary values, secondary keys, and secondary CRC values. `KeyGenerator` tracks existing and non-existing values within a per-thread subrange. Public overrides map the generic stress-test interface to this workload. Protected helpers choose/generate `a` and `c` values, process recovered prepared transactions, write commit-time metadata, commit with optional timestamped snapshot, and set up read snapshots. Private `KeySpaces` serializes persisted range bounds. `InvariantChecker` validates field widths, and `MultiOpsTxnsStressListener` verifies pk/sk consistency after flush and compaction.

## Control flow
The comments specify five logical transactions: primary-key update, secondary-key update, primary-index-value update, point lookup, and range scan. The class overrides generic write/delete/range-delete/ingest paths as unsupported or no-op because this workload only mutates through its custom transaction bodies. Listener callbacks short-circuit after shutdown starts and otherwise call fast verification for CF 0.

## State and persistence behavior
Record format is persisted directly in RocksDB: primary key is index id plus big-endian `a`, primary value is little-endian fixed32 `b,c`, secondary key is index id plus big-endian `c,a`, and secondary value is CRC32 of the secondary key. The `KeySpaces` struct persists lower/upper bounds for `a` and `c` in an external file. Runtime key-generator vectors are in-memory only and rebuilt by preload or scan.

## Dependencies and integration points
The header depends on `db_stress_common.h`, `util/atomic.h`, `StressTest`, `EventListener`, RocksDB transaction abstractions from the broader include graph, and thread/status/stat interfaces from db_stress. Factory functions are implemented in the `.cc` file and selected by the main tool when `FLAGS_test_multi_ops_txns` is set.

## Risks and test signals
The header captures several constraints that must remain true: index IDs must sort primary before secondary, record fields must stay 4 bytes, and current implementation uses only the default CF. Listener verification can run while `TransactionDB::Open()` is still completing, so the implementation must tolerate `db_` not yet being published. Tests should validate encode/decode round trips, CRC checks, unsupported generic operations, per-thread key generator invariants, listener shutdown behavior, and option gates for one-CF TransactionDB operation.
