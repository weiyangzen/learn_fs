# sources/storage-engines/wiredtiger/test/suite/test_layered_schema08.py

## Purpose

This suite verifies that shared metadata queue operations are deferred until checkpoint processing. It also tests operations enqueued concurrently after checkpoint prepare, which must remain deferred until the next checkpoint.

## Important APIs, Types, and Functions

The class extends `checkpoint_util`, uses `wtthread.Thread`, and defines URI helpers for logical, stable, layered, table, and colgroup metadata names. `check_shared_metadata` scans `file:WiredTigerShared.wt_stable` and asserts expected containment or absence. Scenarios cover `layered:` and `table:` layered forms.

## Control Flow

Basic tests show create does not appear in shared metadata until checkpoint, drop remains visible until checkpoint, create+drop in the same checkpoint leaves no entry, and extra checkpoints without schema changes leave metadata unchanged. Concurrent tests use `timing_stress_for_test=[checkpoint_slow]` and `wait_for_checkpoint_start()` so a create or drop occurs after checkpoint prepare. The first checkpoint skips the newly deferred operation; the next checkpoint applies it. The drop case additionally configures fast dhandle sweep and uses `checkpoint_wait=false` so the drop can proceed during a checkpoint.

## State, Persistence, and Dependencies

State includes deferred metadata queue entries, checkpoint prepare/end phases, shared metadata table contents, dhandle sweep state, and timing stress configuration. Dependencies are `time`, `wiredtiger`, `wttest`, `wtthread`, `checkpoint_util`, `helper_disagg`, and `wtscenario`.

## Risks and Test Signals

Risks include applying schema operations too early, losing queue entries across checkpoints, mishandling create/drop pairs, and races between checkpoint and schema operations. Signals are direct shared metadata containment checks before and after each checkpoint, plus thread synchronization around checkpoint start.
