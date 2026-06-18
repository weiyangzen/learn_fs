# sources/storage-engines/tikv/components/backup-stream/src/metadata/test.rs

## Purpose
`metadata/test.rs` contains test-only helpers and integration-style tests for `MetadataClient` using the in-memory `SlashEtcStore`.

## Important APIs, types, and functions
- `test_meta_cli` creates a `MetadataClient<SlashEtcStore>` with store id 42.
- `simple_task` builds a `StreamTask` with name, start/end ts, noop storage backend, and wildcard table filter.
- `assert_range_matches` and `task_matches` compare decoded ranges and task sets.
- Tests cover basic range insertion, watch events, progress computation, storage checkpoint key format, storage checkpoint round trip, and idempotent initialization.

## Control flow
The tests write task info and ranges through `insert_task_with_range`, then read through public client APIs. Watch tests capture a revision from `get_tasks`, subscribe from the next revision, write and delete tasks, cancel the watch, and collect emitted events. Progress tests verify fallback to task start ts, local checkpoint updates, and behavior for another store with no checkpoint.

## State and persistence behavior
All persistence is in-memory through `SlashEtcStore`. The tests exercise durable key layout and value encoding logic as if it were persisted in a metadata backend.

## Dependencies and integration points
Depends on `kvproto::brpb` for task storage protobuf fields, Tokio tests, stream collection, `MetadataEvent`, metadata keys, and `SlashEtcStore`. These helpers support other crate tests because the module is public but cfg-test gated.

## Risks and edge cases
- The helpers use fixed store id 42 unless a test manually creates another client.
- Because the backing store is an approximation, tests may not reveal PD-specific unsupported transaction or pagination behavior.
- `task_matches` compares only task names, not all task fields.

## Test signals
The file itself is the test signal for metadata behavior. It validates task/range APIs, watch conversion to `MetadataEvent`, global progress selection, storage checkpoint path generation, storage checkpoint reads/writes, and `init_task` not rolling progress backward.
