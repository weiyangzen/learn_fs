# sources/storage-engines/wiredtiger/test/csuite/wt9199_checkpoint_txn_commit_race/main.c

## Purpose
WT-9199 creates a race between a committing timestamped transaction and checkpoint stable timestamp selection. It verifies that a transaction whose commit timestamp becomes invalid relative to stable timestamp fails rather than being omitted from a checkpoint incorrectly.

## Important APIs, Types, and Functions
- Connection config enables `timing_stress_for_test=[commit_transaction_slow, prepare_checkpoint_delay]`.
- `thread_func_insert_txn` inserts 1000 records in one transaction, sets stable timestamp to 50, signals `inserted`, then attempts commit at stable+20 and expects `EINVAL`.
- `thread_func_checkpoint` waits for `inserted`, advances stable by 20, sleeps to let commit validate timestamp, checkpoints, and queries `last_checkpoint`.
- Shared globals: `global_stable_ts` and volatile `inserted`.

## Control Flow
`main` parses test options and calls `run_test`. `run_test` recreates the home, opens WiredTiger, creates the row-store table, starts insert and checkpoint threads, joins them, closes session and connection, and optionally removes the home.

## State and Persistence Behavior
The inserted records are part of a transaction expected to fail commit with `EINVAL`; durable user data is not the validation target. Persistent checkpoint timestamp state is queried to ensure checkpoint completed in the raced window.

## Dependencies and Integration Points
The test depends on timing-stress hooks for commit and checkpoint preparation, timestamp validation, pthread scheduling, and the C API transaction timestamp configuration.

## Risks and Test Signals
The central assertion is `commit_transaction` returning `EINVAL`. If the commit succeeds or returns a different error, the test fails. Thread coordination is intentionally minimal and timing-stress-driven, so behavior relies on the configured delays.
