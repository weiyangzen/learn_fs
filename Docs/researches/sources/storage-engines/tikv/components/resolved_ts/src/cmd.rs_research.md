# sources/storage-engines/tikv/components/resolved_ts/src/cmd.rs

Purpose: this file converts raftstore observed command batches into resolved-ts change logs. It extracts transactional row-level changes from write/default/lock CF mutations so resolved-ts tracking can update locks and commits without reinterpreting full raft commands elsewhere.

Important APIs and types:
- `ChangeRow` represents decoded transactional effects: `Prewrite`, `Commit`, `OnePc`, and `IngestSsT`.
- `ChangeLog` wraps command-level outcomes: raft command error, row changes at an apply index, or admin command type.
- `ChangeLog::encode_change_log(region_id, CmdBatch)` maps observed raft commands for a region into `ChangeLog` values.
- `decode_write` and `decode_lock` parse txn write and lock records and filter unsupported/non-lock-relevant types.
- Internal `KeyOp` and `RowChange` group CF-level mutations by logical key before row encoding.
- `lock_only_filter` drops default-CF-only data from command batches when observe level is `LockRelated`.

Control flow:
- `encode_change_log` iterates a `CmdBatch` by region. Error responses become `ChangeLog::Error`; admin requests become `ChangeLog::Admin`; normal write batches are grouped and encoded into rows.
- It detects one-phase commit from `WriteBatchFlags::ONE_PC`.
- `group_row_changes` scans raft requests, records write CF puts by truncating commit timestamps from encoded keys, lock CF puts/deletes by raw key, default CF puts as unmatched defaults keyed by truncated timestamp, and `IngestSst` as a batch flag.
- After scanning, default values are attached only to keys that also had a lock or write row.
- `encode_rows` matches `(write, lock, default)` patterns into prewrite/commit/one-pc/rollback rows. Rollback commits intentionally clear commit ts; lock deletes become rollback commits with unknown start ts.
- `lock_only_filter` respects `ObserveLevel`: `None` drops the batch, `All` passes it through, and `LockRelated` retains lock CF, write CF, and ingest SST requests.

State and persistence behavior:
- This file has no persistent state. It is pure transformation over observed raft command data.
- Correctness depends on raft apply command ordering and indexes supplied by `CmdBatch`; row logs preserve the apply index for downstream resolver tracking.

Dependencies and integration points:
- Uses raftstore coprocessor `CmdBatch`, `Cmd`, and `ObserveLevel`; resolved-ts observer/endpoint code consumes `ChangeLog` and `ChangeRow`.
- Uses engine CF constants for lock/write/default filtering.
- Uses `txn_types` decoders for `WriteRef`, lock type parsing, `Lock`, `Write`, timestamps, and write batch flags.
- `ChangeLog` is re-exported by the `resolved_ts` crate and referenced by `endpoint.rs` when tracking applied changes.

Risks and edge cases:
- Unexpected row patterns panic, so grouping assumptions must match TiKV MVCC write batch generation.
- `decode_write` skips rewritten records with `gc_fence` and asserts they are overlapped rollbacks; this deliberately ignores some overlapped rollback writes.
- Only Put/Delete/Rollback write types and Put/Delete locks are relevant. Other lock types, including shared locks, are skipped.
- Default CF values are only attached when a matching lock/write mutation is present; unmatched default writes are ignored for resolved-ts tracking.
- `IngestSsT` is represented as a row marker because it can affect lock visibility outside normal row decoding.

Test signals:
- `test_cmd_encode` builds MVCC operations through TiKV test engines and verifies prewrite, commit, rollback, large default value attachment, one-pc rows, ingest SST marker behavior, and the known absence of an overlapped rollback row in one scenario.
