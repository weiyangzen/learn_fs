# sources/storage-engines/wiredtiger/test/cppsuite/src/main/database_operation.cpp

## Purpose
Implements the default `database_operation` workload methods used by cppsuite tests: population, checkpointing, background compaction, custom no-op work, insert/read/remove/update loops, and default validation dispatch.

## Important APIs, Types, And Functions
Key entry points are `database_operation::populate`, `background_compact_operation`, `checkpoint_operation`, `custom_operation`, `insert_operation`, `read_operation`, `remove_operation`, `update_operation`, and `validate`. A file-local `populate_worker` partitions collections across `thread_worker` instances and inserts deterministic padded keys with pseudo-random values.

## Control Flow
`populate` validates collection/key/value/thread configuration, creates collections through the `database` model, starts one `thread_worker` per configured thread, joins via `thread_manager`, and deletes workers. Runtime operations loop while `thread_worker::running()` remains true. Insert workers keep one cursor per assigned collection and commit when `thread_worker::can_commit()` says the randomized operation target is reached. Read workers cache cursors per collection and walk with `next`, resetting at `WT_NOTFOUND`. Remove workers use paired random and normal cursors because random cursors cannot remove. Update workers select a random key below the model's current key count and call the generic tracked update path.

## State And Persistence Behavior
The file mutates WiredTiger tables through cursors and keeps the in-memory collection key count in sync only after successful insert commits. Transactions are explicitly begun, committed, or rolled back through `thread_worker`, which also records operation-tracking rows and timestamps. Cursor resets are used deliberately to avoid pinning pages or history. Background compact is enabled through `WT_SESSION::compact` with `background=true`; checkpointing periodically calls `WT_SESSION::checkpoint`.

## Dependencies And Integration Points
Depends on `thread_worker`, `database`, `configuration`, `timestamp_manager`, `operation_tracker`, `connection_manager`, `validator`, `random_generator`, `thread_manager`, and WiredTiger error codes such as `WT_NOTFOUND` and `WT_ROLLBACK`. It is the default behavior inherited by `test`, and concrete tests override individual methods to alter workload shape.

## Risks And Test Signals
The implementation assumes `collection_count >= thread_count` for insert/populate partitioning, so configs with too many threads assert. Key uniqueness depends on `key_count <= pow(10, key_size)`. Read operations roll back by operation count rather than committing. Update tracking uses `tracking_operation::INSERT` for value replacement, so validation treats the latest value as an upsert-style final state. Successful signals are normal thread completion, `SUCCESS` from the harness, operation tracker rows for validation, and nonzero compact/checkpoint activity where configured.
