# sources/storage-engines/tikv/components/sst_importer/src/sst_writer.rs

## Purpose
This file implements SST writers used by the local SST importer to materialize incoming import batches into RocksDB SST files. It has two paths: `TxnSstWriter` for transactional KV import and `RawSstWriter` for raw KV import. The code sits between protobuf import requests (`WriteBatch`, `RawWriteBatch`, `Pair`) and the engine abstraction (`KvEngine::SstWriter`), adding TiKV key encoding, API-version checks, MVCC write records, TTL encoding, file finalization, encryption metadata handoff, and import metrics.

## Important APIs, Types, And Functions
`SstWriterType` distinguishes transactional and raw writers for diagnostics. `TxnSstWriter<E>` owns separate default-CF and write-CF SST writers plus entry/byte counters, output `ImportPath`s, `SstMeta`s, optional `DataKeyManager`, selected `ApiVersion`, and `txn_source`. `TxnSstWriter::write` validates nonzero commit timestamps, checks key mode by API version, appends commit timestamps to raw keys, and delegates to `put`. `TxnSstWriter::put` writes large values to default CF and always writes a serialized `txn_types::Write` record to write CF. `finish` closes non-empty writers, saves output files through `ImportPath::save`, and returns the matching metas.

`RawSstWriter<E>` writes raw key/value pairs only to default CF. `RawSstWriter::write` uses `match_template_api_version!` to encode raw keys and values, applies TTL only for API versions where TTL is enabled, and emits deletes via SST delete records. `RawSstWriter::finish` only emits metadata when `default_entries > 0`, although delete counts are tracked separately.

## Control Flow And State
Both writers are stateful accumulators. Each batch mutates counters and the underlying SST writer, then `finish` consumes the writer. Transactional import rejects zero commit TS before writing anything; per-pair operations use `PairOp::Put` and `PairOp::Delete`. Short transactional values are embedded into write CF records, while long values are persisted in default CF and referenced from write CF. Raw import derives an optional expire timestamp from the batch TTL and API support, then encodes `RawValue` before writing.

## Persistence And Integration Points
Persistence happens through engine-trait SST writer calls and `ImportPath::save`, which is where encrypted-file bookkeeping can be applied through `DataKeyManager`. Keys are wrapped with `keys::data_key`, so the produced SST contents are in TiKV's internal data-key namespace. The module integrates with `api_version`, `txn_types`, `engine_traits`, `kvproto::import_sstpb`, importer metrics, and importer construction methods such as `SstImporter::new_txn_writer` and `new_raw_writer`.

## Risks And Test Signals
Key-mode validation is critical for API V2: transactional import accepts Txn/TiDB key modes, raw import accepts Raw mode only. Raw TTL handling must reject TTL for API V1 without TTL support. `RawSstWriter::finish` ignores delete-only batches because it checks only `default_entries`; callers relying on delete-only raw SSTs should be aware of that behavior. Tests cover txn source propagation, short/large/delete txn writes, zero commit TS rejection, raw TTL encoding for V1ttl and V2, TTL-disabled errors, V1 raw writes, invalid V2 raw key mode, and valid/invalid V2 txn keys.
