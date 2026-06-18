# sources/storage-engines/raft-engine/examples/append_compact_purge.rs

## Purpose
Demonstrates a continuously running workload that appends Raft entries, stores last-index messages, compacts regions, and calls purge to exercise raft-engine rewrite/purge behavior.

## Important APIs, Types, And Functions
Defines `MessageExtTyped` implementing `MessageExt` for raft-rs `Entry`. Uses `Config`, `Engine`, `LogBatch`, `ReadableSize`, `get_message`, `add_entries`, `put_message`, `write`, `compact_to`, and `purge_expired_files`.

## Control Flow
The example opens `append-compact-purge-data` with a low compression threshold and 2GB purge threshold. It repeatedly chooses normally distributed region IDs and compact offsets, increments each region's persisted `RaftLocalState.last_index`, appends a 32KB entry, writes the batch, and periodically compacts based on the index. After each 1024 writes, it purges expired files and force-compacts returned regions close to their last index.

## State And Persistence Behavior
It creates a real raft-engine data directory, persists entries and per-region last-index messages, records compaction commands, and physically rewrites/purges log files. The loop is infinite, so disk usage and purge behavior are the demonstration target.

## Dependencies And Integration Points
Integrates with kvproto `RaftLocalState`, raft-rs `Entry`, rand normal distributions, env_logger, and the main engine append/compact/purge APIs.

## Risks And Edge Cases
The infinite loop can consume disk indefinitely if purge behavior is broken or the process is left running. Random region IDs can cast negative normal samples to large `u64` values. The example unwraps all errors and is not production-safe.

## Test Signals
Operational signals are debug logs and printed compact/force-compact messages, plus stable engine behavior under sustained append/compact/purge load.
