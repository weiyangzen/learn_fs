# sources/storage-engines/wiredtiger/test/cppsuite/tests/background_compact.cpp

## Purpose
Defines a workload that encourages and validates WiredTiger background compaction by alternating insert/truncate activity with maintenance windows and compact enable/disable cycles.

## Important APIs, Types, And Functions
`class background_compact : public test` overrides `custom_operation`, `remove_operation`, `insert_operation`, `background_compact_operation`, and `validate`. It uses a volatile `maintenance_window` flag, metrics monitor statistics, random cursors, truncate ranges, and compact configuration strings.

## Control Flow
The custom operation toggles the maintenance window after sleeping. Remove operation pauses during maintenance, samples collection statistics, skips truncation if reusable space already exceeds a threshold, otherwise repeatedly chooses random keys and truncates small ranges until roughly 20 percent of entries are removed or retries are exhausted, then checkpoints. Insert operation mirrors default insertion but also pauses during maintenance. Background compact operation toggles `session->compact` between `background=true` with a free-space target and `background=false`.

## State And Persistence Behavior
The test mutates collections through inserts and truncates, forces checkpoints, and changes background compact server state. It uses operation tracking for mutations but supplies custom validation focused on compaction statistics rather than full data replay.

## Dependencies And Integration Points
Depends on constants/logger/random generator, base test, validator include, `metrics_monitor`, `connection_manager`, and WiredTiger statistics. It integrates with configured background compact debug mode and free-space target.

## Risks And Test Signals
`maintenance_window` is volatile rather than atomic, so it is a lightweight coordination flag but not a strong synchronization primitive. Validation asserts multiple background compact statistics are greater than zero: bytes recovered, EMA, compact writes, files tracked, skipped, and success. Workload effectiveness depends on file statistics, checkpoint timing, and enough runtime for compact to act.
