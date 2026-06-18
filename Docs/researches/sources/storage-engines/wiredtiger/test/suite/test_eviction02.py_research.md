# sources/storage-engines/wiredtiger/test/suite/test_eviction02.py

## Purpose

Verifies clean eviction removes obsolete time-window metadata within configured per-checkpoint cleanup limits.

## Important APIs, Types, and Functions

`test_eviction02` inherits `eviction_util`, sets scenario-specific `heuristic_controls`, and uses `populate`, `evict_cursor_tw_cleanup`, timestamp helpers, and statistics `cache_eviction_dirty_obsolete_tw`.

## Control Flow

Across ten rounds it inserts more timestamped data, makes it stable, checkpoints it clean, advances oldest so prior time windows become obsolete, then forces clean eviction. It tracks per-iteration cleanup deltas and final data-source/connection stats.

## State and Persistence Behavior

State is timestamped page metadata rather than user-visible values. Checkpoints reset the cleanup budget, and stats accumulate cleanup work at data-source and connection scope.

## Dependencies and Integration Points

Depends on `eviction_util`, `wiredtiger.stat`, scenario generation, statistics logging, and heuristic controls.

## Risks and Maintenance Signals

Eviction may not clean work every iteration, so the test only bounds diffs and requires eventual work. The threshold allows stale stat buffer tolerance.

## Test Signals

Signals are zero cleanup when disabled, bounded cleanup when enabled, and final positive btree/connection cleanup stats.
