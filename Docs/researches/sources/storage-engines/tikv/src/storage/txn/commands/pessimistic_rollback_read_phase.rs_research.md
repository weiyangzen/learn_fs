# sources/storage-engines/tikv/src/storage/txn/commands/pessimistic_rollback_read_phase.rs

## Purpose
Scans lock-CF for pessimistic locks matching a transaction start timestamp and `for_update_ts` bound, then emits a write-phase rollback command for the batch.

## Important APIs, Types, and Functions
`PessimisticRollbackReadPhase` contains `start_ts`, `for_update_ts`, and optional `scan_key`. It is readonly, tagged `pessimistic_rollback_read_phase`, and returns the same callback type as `PessimisticRollback`. It uses `MvccReader::scan_locks` with `RESOLVE_LOCK_BATCH_SIZE`.

## Control Flow
The read phase scans forward from `scan_key`, filtering locks whose start ts matches, which are pessimistic, and whose lock `for_update_ts` is not newer than the request. If no locks are found, it returns an empty multi-result. Otherwise it builds `PessimisticRollback` with the found keys and a next scan key if more locks remain.

## State and Persistence
No writes occur in this phase. It accumulates reader statistics and records key-read histogram counts. Persistence is delegated to the emitted write command.

## Dependencies and Integration Points
Used when `PessimisticRollbackRequest` has no explicit keys. It integrates with scan lock read-time metrics and the scheduler's `NextCommand` chaining.

## Risks and Test Signals
Risks include scan filter mismatch with the write phase and continuation-key duplication or omission. Tests verify reading shared pessimistic locks, respecting `for_update_ts`, ignoring nonmatching start timestamps, and bypassing shared prewrite locks.
