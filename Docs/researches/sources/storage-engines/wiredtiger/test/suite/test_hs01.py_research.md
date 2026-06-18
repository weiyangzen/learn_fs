# sources/storage-engines/wiredtiger/test/suite/test_hs01.py

## Purpose

Broad history-store durability test for updates and modifies across checkpoints, crash-style backup recovery, precise versus fuzzy checkpoint behavior, and timestamp visibility.

## Important APIs, Types, and Functions

Defines scenario products over key formats and `precise_checkpoint`. Helpers include `large_updates`, `large_modifies`, `durable_check`, and `get_stat`; uses `wiredtiger.Modify` and history-store stats.

## Control Flow

The test inserts 10k rows, checkpoints, holds an old reader while applying large updates so checkpoint writes old versions to history store, verifies stats and recovery, repeats with modify chains, then applies timestamped updates beyond stable timestamp and checks recovered visibility before and after advancing stable.

## State and Persistence Behavior

State spans user table pages, history-store inserts, stable/oldest timestamps, long-running readers, and backup-copy recovery into `BACKUP`. Precise checkpoints keep unstable updates in memory where fuzzy checkpoints may move them to HS.

## Dependencies and Integration Points

Depends on `copy_wiredtiger_home`, `SimpleDataSet`, `wiredtiger.stat`, scenario generation, and timestamp helpers. Disaggregated mode skips the fuzzy durable check.

## Risks and Maintenance Signals

Stat exactness is tied to row counts and reconciliation behavior. Backup recovery checks only first cursor value, not every row.

## Test Signals

Signals are exact HS insert/key/update stats, recovered values after simulated recovery, and stable timestamp visibility across checkpoint modes.
