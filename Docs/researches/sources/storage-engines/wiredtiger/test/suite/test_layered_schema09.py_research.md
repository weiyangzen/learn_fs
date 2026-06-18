# sources/storage-engines/wiredtiger/test/suite/test_layered_schema09.py

## Purpose

This test verifies persistence of the stable disaggregated schema epoch in checkpoints. It distinguishes the current stable schema epoch set by the caller from the last schema epoch recorded in the latest checkpoint.

## Important APIs, Types, and Functions

`assertEpochEqual` queries `get=stable_disaggregated_schema_epoch`; `assertLastCheckpointEpochEqual` queries `get=last_disaggregated_schema_epoch`. The connection runs as a disaggregated leader with statistics and `lose_all_my_data=true`. The test creates a layered table so checkpointing exercises disaggregated storage.

## Control Flow

The first checkpoint before setting an epoch records last checkpoint epoch 0. The test then sets oldest, stable, and stable schema epoch to 10, checkpoints, and expects last checkpoint epoch 10. After restart, the last checkpoint epoch remains 10. It advances timestamps and epoch to 30, checkpoints, and expects 30. A checkpoint changing only stable timestamp leaves last epoch at 30. A checkpoint changing only the schema epoch to 40 updates last checkpoint epoch to 40. A final restart confirms the current epoch resets to 0 while the last checkpoint epoch persists as 40.

## State, Persistence, and Dependencies

State crosses queryable timestamp state, checkpoint metadata, restart, and local file removal. Dependencies include `wttest`, `helper_disagg`, and `wiredtiger.stat` though the stat import is not used.

## Risks and Test Signals

Risks include failing to write schema epoch into checkpoint metadata, incorrectly restoring it as current mutable state, or skipping checkpoints when only the schema epoch changes. Signals are timestamp equality assertions before and after checkpoints and restarts.
