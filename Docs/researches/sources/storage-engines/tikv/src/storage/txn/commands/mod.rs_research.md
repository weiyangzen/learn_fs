# sources/storage-engines/tikv/src/storage/txn/commands/mod.rs

## Purpose
Defines the transaction command facade used by TiKV storage scheduling. It declares command modules, re-exports concrete command types, maps incoming protobuf RPC requests into typed commands, and dispatches commands into read or write execution.

## Important APIs, Types, and Functions
`Command` is the central enum covering prewrite, commit, rollback, resolve lock, check status, raw operations, flashback, flush, and test pause commands. `TypedCommand<T>` reifies the callback result type. `ResponsePolicy`, `WriteResult`, `WriteResultLockInfo`, `ReleasedLocks`, `CommandExt`, `WriteContext`, `ReaderWithStats`, `ReadCommand`, and `WriteCommand` are shared command contracts.

## Control Flow
`From<...Request>` implementations translate RPC fields into command constructors, handling details such as async commit secondaries, pessimistic actions, wake-up mode, resolve-lock read phase versus lite write phase, empty-key pessimistic rollback scans, and flashback prepare/finish phases. `Command::process_read` and `process_write` match enum variants to concrete trait implementations, panicking on unsupported phase use.

## State and Persistence
`WriteResult` is the persistence handoff: it carries `WriteData`, row counts, process result, lock info for wait, released locks for wakeup, new lock info, raw key guards, response timing, and known transaction status cache updates. `WriteContext` supplies lock manager, concurrency manager, statistics, extra operations, async prewrite flag, raw extensions, and transaction-status cache.

## Dependencies and Integration Points
This file is the integration point between kvproto RPCs, scheduler latches/deadlines/priority/resource control, MVCC command implementations, lock manager, raw API timestamp providers, metrics, and callback typing. `ReaderWithStats` ensures snapshot read statistics are merged on drop.

## Risks and Test Signals
Risks include request-field translation bugs, missing enum dispatch when adding commands, wrong response policy, and inaccurate latch or byte accounting. The `test_util` module provides reusable prewrite, commit, rollback, pessimistic lock, and API V2 timestamp helpers used across command tests.
