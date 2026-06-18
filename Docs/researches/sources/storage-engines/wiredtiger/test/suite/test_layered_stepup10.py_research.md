# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup10.py

## Purpose
Regression test for disaggregated btree handle state across two step-down and step-up cycles on the same connection.

## APIs, Types, And Functions
Defines `test_layered_stepup10` with small and large oplog sizes. It uses `Oplog`, layered table creation, role `Connection.reconfigure`, stable timestamps, and checkpoints with `precise_checkpoint=true` and `preserve_prepared=true`.

## Control Flow, State, And Persistence
The test writes and checkpoints a stable baseline, reconfigures to follower, applies batch 2 into ingest, promotes to leader and checkpoints to drain, then repeats follower write and leader drain for batch 3. It then verifies all three batches on the current leader. Persistence focus is clearing ingest and refreshing btree handles so stale readonly state does not corrupt checkpoint block-size accounting on the second cycle.

## Dependencies, Integration, Risks, And Test Signals
Integrates disaggregated btree handle lifecycle, oplog replay, and checkpoint size accounting. The risk is a handle left readonly or outdated across promotion, causing skipped checkpoints or block-size assertion failure. The signal is successful second cycle checkpoint and complete Oplog verification.
