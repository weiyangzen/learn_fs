# sources/storage-engines/wiredtiger/test/suite/test_hs07.py

## Purpose

Tests that the history-store sweep server removes obsolete entries while preserving correct visible data after repeated update/modify cycles.

## Important APIs, Types, and Functions

Defines `large_updates`, `check`, and `test_hs` across column and integer row formats with a small cache and high eviction update triggers.

## Control Flow

The test writes 10k rows at timestamp 1, pins oldest/stable, pushes pages out with an extra table, advances timestamps, sleeps for sweep cleanup, then repeats cycles of modifies and full updates at later timestamps 200 and 300, each time checking reads after sweep.

## State and Persistence Behavior

State includes obsolete HS records, sweep-server cleanup timing, oldest/stable timestamp advancement, and extra-table eviction pressure.

## Dependencies and Integration Points

Depends on `time.sleep`, `wiredtiger.Modify`, `SimpleDataSet`, scenario generation, and the background history-store sweep server.

## Risks and Maintenance Signals

The three 10-second sleeps make runtime long and environment-dependent. It does not assert sweep stats directly; correctness after sweep is the main signal.

## Test Signals

Signals are successful full-table scans at expected values after timestamp advancement and sweep windows, plus ignored long-eviction stdout warnings.
