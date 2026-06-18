# sources/storage-engines/wiredtiger/test/suite/test_prepare33.py

## Purpose

Tests checkpoint handling for rolled-back prepared transactions that include tombstones.

## Important APIs, Control Flow, and State

The test creates initial data, checkpoints, then a prepared transaction updates many keys and repeatedly removes key 1, prepares at timestamp 70 with a prepared ID, and rolls back at timestamp 80. With stable 40, checkpoint should not write the prepare. With stable 75, checkpoint should write prepared start and stop transaction metadata. With stable 85, rollback is stable, so checkpoint should skip the aborted prepared stop information while writing committed start metadata.

## Dependencies, Risks, and Test Signals

Dependencies are preserve-prepared base config, prepared IDs, and detailed reconciliation stats such as start/stop txn and durable start/stop timestamps. The risk is mishandling tombstone time-window fields after rollback. Signals are granular stat expectations at pre-prepare, between prepare/rollback, and post-rollback stable timestamps.
