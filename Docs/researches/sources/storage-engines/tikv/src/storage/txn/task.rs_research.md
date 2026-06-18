# sources/storage-engines/tikv/src/storage/txn/task.rs

## Purpose
`task.rs` defines the scheduler's `Task` wrapper around a transaction `Command`. It attaches a command ID, tracker token, optional raft snapshot extra operation, and memory-quota ownership to command execution. The wrapper provides the narrow dispatch points used by the scheduler to process read and write commands once a snapshot is available.

## Important APIs, types, and functions
`Task` stores `cid`, `tracker_token`, `cmd: Option<Command>`, `extra_op: ExtraOp`, and optional `OwnedAllocated` memory quota. `Task::allocate` is the normal constructor. It captures the current TLS tracker token, computes command approximate heap size, reserves that amount from `MemoryQuota`, updates the scheduler memory metric, and returns `MemoryQuotaExceeded` if the command cannot be admitted. `Task::force_create` bypasses quota accounting for internally generated reschedule commands and is documented as a temporary special case.

Accessors expose command ID, tracker token, immutable/mutable command references, and extra operation. `set_extra_op` records snapshot-provided `ExtraOp` after snapshot acquisition and before command processing. `process_write` consumes the command and calls `Command::process_write` with a snapshot and `WriteContext`; `process_read` consumes the command and calls `Command::process_read` with a snapshot and mutable statistics.

## Control flow
`TxnScheduler::run_cmd` creates tasks with `Task::allocate`. Once latches are acquired and a snapshot is fetched, `TxnScheduler::execute` updates the command context from snapshot metadata, calls `set_extra_op`, and then delegates to `process_read` or `process_write` through the scheduler's higher-level flow. When read/write processing begins, the command is taken out of the `Option`, ensuring a task is processed once.

Internal scheduler paths such as `NextCommand` scheduling and resumed pessimistic-lock commands use `force_create`, avoiding a second quota charge for transitional commands until the surrounding scheduler callback flow is refactored.

## State and persistence behavior
The task itself does not persist data. Its `OwnedAllocated` field is stateful: memory remains charged while the task exists and is freed automatically when the task is dropped. This allows queued commands blocked on latches to consume quota and prevents unbounded request accumulation. `extra_op` carries snapshot transaction-extra behavior into write processing, where command handlers may include old-value or CDC-related extra data in `WriteData`.

## Dependencies and integration points
`Task` depends on `Command`, `WriteContext`, `WriteResult`, `ProcessResult`, engine snapshots, lock managers, storage statistics, memory quota utilities, tracker TLS, kvproto `ExtraOp`, and scheduler memory metrics. It is private to the transaction scheduler module and forms the boundary between scheduling mechanics and command execution.

## Risks and edge cases
Both `cmd()` and `cmd_mut()` unwrap the command option, and `process_read`/`process_write` take it. Any attempt to inspect a task after processing would panic. `force_create` intentionally skips quota accounting, so expanding its use beyond reschedule flows could bypass scheduler memory backpressure. `allocate` updates the in-use metric after successful allocation; future allocation or drop paths must keep that metric aligned with quota state.

## Test signals
`test_alloc_memory_quota` converts a default prewrite request into a command, allocates a task against a large quota, asserts quota usage becomes nonzero, drops the task, and asserts quota returns to zero. Scheduler tests in `scheduler.rs` further verify that queued commands are rejected under configured memory quota and that quota is freed after completion.
