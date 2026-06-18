# sources/storage-engines/wiredtiger/test/suite/test_hs24.py

## Purpose

Races no-timestamp fixes with history-store checkpointing to ensure crash recovery sees consistent data-store and history-store checkpoints.

## Important APIs, Types, and Functions

Defines `test_hs24` scenarios over key formats and timing stress (`checkpoint_slow` or `history_store_checkpoint_delay`), `moresetup`, `missing_ts_deletes`, `missing_ts_commits`, and two race tests.

## Control Flow

Both tests write two timestamped versions per row, set stable timestamp, launch a worker thread that performs no-timestamp deletes or commits across all rows, checkpoint while that thread runs, join it, then simulate crash restart. Post-restart reads at timestamps 5/4 or 4 validate that checkpoint state is internally consistent despite partial race progress.

## State and Persistence Behavior

State includes concurrent no-timestamp operations, timing-stressed checkpoint/HS checkpoint windows, crash-restart recovery, and timestamped historical reads.

## Dependencies and Integration Points

Depends on `wtthread`, `simulate_crash_restart`, `wiredtiger.WT_NOTFOUND`, scenario generation, timing stress config, and multi-session worker threads.

## Risks and Maintenance Signals

The race window is encouraged by sleep and timing stress, not fully deterministic. Assertions allow a prefix-like split between rows affected before checkpoint and rows not affected, using `newer_data_visible` transitions.

## Test Signals

Signals are successful crash restart and consistent historical visibility: newer data implies older HS version exists, missing newer data implies older read is also not found or sees only allowed pre-checkpoint values.
