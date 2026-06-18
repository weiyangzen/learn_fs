# sources/storage-engines/tikv/src/storage/txn/commands/flush.rs

## Purpose
Implements `Flush`, a generation-aware prewrite-like command used to flush mutations for the same transaction. It can overwrite an existing same-start-ts lock when the incoming generation is newer, while ignoring out-of-order generations.

## Important APIs, Types, and Functions
`Flush` carries `start_ts`, primary key, mutations, generation, TTL, and assertion level. `flush` builds `TransactionProperties` and calls `prewrite_with_generation`. It returns `Vec<StorageResult<()>>` through `ProcessResult::MultiRes`. Old values are collected with `insert_old_value_if_resolved`.

## Control Flow
`process_write` rejects generation zero, creates transaction/reader state, and delegates to `flush`. The per-mutation loop runs generation-aware prewrite with pessimistic checks skipped. Write conflicts with later commits and key-lock errors are passed through `check_committed_record_on_err`; assertion failures are delayed so other errors take precedence. `GenerationOutOfOrder` is logged and ignored.

## State and Persistence
Successful flushes write lock-CF prewrite state and possibly overwrite older generated lock content for the same transaction. `TxnExtra` includes old values, with `one_pc` and flashback disabled. Guards are asserted empty. Response policy is `OnApplied`; no txn-status cache entry is emitted.

## Dependencies and Integration Points
Reuses core prewrite action logic, `TransactionProperties`, assertion checking, old-value collection, and command conversion from `FlushRequest` in `mod.rs`. It interacts with normal commit paths: tests commit flushed locks with the ordinary commit command.

## Risks and Test Signals
Key risks are generation ordering, interaction with existing locks, assertion failure priority, and old-value correctness. Tests cover normal flush/commit, write conflicts against flush/pessimistic/prewrite, overwriting with newer generation, ignoring older generation, insert existence checks, and assertion-level overwrite behavior.
