# sources/storage-engines/raft-engine/src/consistency.rs

## Purpose
Implements a replay machine that checks recovered log streams for holes in Raft entry indexes.

## Important APIs, Types, And Functions
`ConsistencyChecker` stores per-raft-group `(first_index, last_index)` ranges and a `corrupted` map from raft group ID to last valid index. It exposes `finish` and implements `ReplayMachine` through `replay` and `merge`.

## Control Flow
During `replay`, the checker scans each `LogItemBatch`, considers only `EntryIndexes` content, extracts incoming first/last indexes, initializes a group range when first seen, and records corruption if the next incoming first index is more than one past the current last index. `merge` combines checker outputs from recovered files or queues and detects holes between merged ranges as well as holes already found in the right-hand checker.

## State And Persistence Behavior
The checker does not mutate persisted files. It derives transient corruption diagnostics from durable log contents and returns the earliest observed last intact index per raft group.

## Dependencies And Integration Points
Depends on `ReplayMachine`, `LogItemBatch`, `LogItemContent`, `FileId`, and `LogQueue`. `Engine::consistency_check_with_file_system` uses it with `RecoveryMode::TolerateAnyCorruption`.

## Risks And Edge Cases
Head or tail corruption cannot be detected by this range continuity method. Out-of-order replay or incorrect merge order could create false positives or miss holes. The checker reports only the first last-valid index per group.

## Test Signals
Signals are CLI/check outputs and engine consistency-check tests that expect sorted corrupted raft-group pairs.
