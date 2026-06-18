# sources/storage-engines/tikv/src/storage/txn/commands/mvcc_by_start_ts.rs

## Purpose
Implements a readonly diagnostic command that finds the first committed key whose write record has the requested start timestamp, then returns that key's MVCC history.

## Important APIs, Types, and Functions
`MvccByStartTs` stores `start_ts` and returns `Option<(Key, MvccInfo)>`. It uses the `start_ts_mvcc` metric tag, marks itself readonly, and has an empty latch. `process_read` uses `MvccReader::seek_ts` followed by `find_mvcc_infos_by_key`.

## Control Flow
The command opens a forward `MvccReader`, seeks write-CF for the first key matching the start timestamp, and if found loads full MVCC info for that key. If no matching write exists, it returns `ProcessResult::MvccStartTs { mvcc: None }`.

## State and Persistence
No writes occur. Reader statistics are added when a key is found; the no-result path returns without explicitly adding stats, so changes here should consider whether that omission is intentional or negligible.

## Dependencies and Integration Points
Constructed from `MvccGetByStartTsRequest`, dispatched as a read command, and used for diagnostics/admin inspection of transaction history.

## Risks and Test Signals
Risks include scan cost over write-CF and subtle statistic accounting differences between found and not-found paths. Functional coverage is likely shared with MVCC diagnostic tests.
