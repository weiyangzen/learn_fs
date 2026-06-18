# sources/storage-engines/wiredtiger/test/suite/test_prepare34.py

## Purpose

Tests preserve-prepared checkpoint behavior for transactions containing `wiredtiger.Modify` operations, for both rollback and commit.

## Important APIs, Control Flow, and State

The rollback test inserts baseline `aaaaa` values, prepares two rounds of large modifies, checkpoints before and after rollback timestamp movement, and verifies reads at timestamp 75 still return the original value. The commit test performs ordered modifies inserting long B and D strings, commits with durable timestamp 90, verifies checkpoints write prepared content when prepare is stable and committed content when durable is stable, handles disaggregated storage page-delta expectations, and checks timestamp 81 reconstructs `D + B + aaaaa`.

## Dependencies, Risks, and Test Signals

Dependencies are `wiredtiger.Modify`, preserve-prepared stats, read timestamps, and hook-specific disagg behavior. Risks include reconstructing modifies incorrectly from preserved prepared cells or writing wrong time-window metadata. Signals are reconciliation stats plus value reconstruction before and after commit.
