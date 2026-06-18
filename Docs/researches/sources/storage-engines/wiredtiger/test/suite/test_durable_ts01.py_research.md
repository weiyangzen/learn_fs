# sources/storage-engines/wiredtiger/test/suite/test_durable_ts01.py

Purpose: tests durable timestamp recovery across restart, ensuring only updates durable at the stable timestamp survive recovery.

Important APIs and control flow: scenarios cover file/table simple datasets, key formats excluding column store, and read isolation modes. The test follows the durable timestamp pattern: checkpoint initial data at stable 100, commit value 111 with durable 220, verify timestamped visibility, commit later value 222 with commit before stable but durable after stable, checkpoint, restart, and verify recovery shows the durable 111 state.

State and persistence: checkpoint and restart are central; recovery should rollback updates whose durable timestamp exceeds stable. The class skips disaggregated storage because RTS does not run during disaggregated recovery.

Dependencies and integration: uses `SimpleDataSet`, `make_scenarios`, timestamp APIs, sessions with isolation variants, and connection reopen/restart behavior.

Risks and test signals: failures indicate recovery/RTS mishandles durable timestamps, especially prepared or checkpointed unstable updates.
