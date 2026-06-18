# sources/storage-engines/wiredtiger/test/suite/test_hs21.py

## Purpose

Tests that idle data handles with active history can be swept/closed without losing historical visibility or changing run write generation during the same process lifetime.

## Important APIs, Types, and Functions

Defines `large_updates`, `check`, `parse_run_write_gen`, and `test_hs`; uses file-manager close settings, connection stats, metadata parsing, and ten tables.

## Control Flow

The test creates ten tables, records each file's `run_write_gen`, writes half-row values at timestamp 2, opens a long-running reader at timestamp 2, writes full-row values at timestamp 100, advances stable, repeatedly checkpoints and polls sweep stats until handles close, then verifies the old reader still sees timestamp 2 data and current reads see timestamp 100 data. It also checks run write gen stability outside disaggregated mode.

## State and Persistence Behavior

State spans multiple table handles, active history newer than oldest, long-running read transactions across handle close/reopen, metadata run-write generation, and sweep statistics.

## Dependencies and Integration Points

Depends on `SimpleDataSet`, `wiredtiger.stat`, metadata cursors, regex parsing, file-manager sweep configuration, and timestamps. Skipped for tiered storage.

## Risks and Maintenance Signals

Polling for sweep closure is timing-sensitive. `final_numfiles=3` assumes only metadata, HS, and lock files remain open. Disaggregated mode relaxes run-write-gen assertion due to a FIXME.

## Test Signals

Signals are sweep close stats, preserved historical reads after handle closure, current data reads, and unchanged run write generation where applicable.
