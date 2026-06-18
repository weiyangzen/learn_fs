# sources/storage-engines/wiredtiger/test/suite/test_prepare_hs02.py

Purpose: exercises prepared insert, update, remove, and checkpointed-key update chains under both commit and rollback resolution to ensure reconciliation and history store paths can handle them.

Important APIs and types: `suite_subprocess`, `make_scenarios`, row and column table configs, cursor item assignment/removal, `prepare_transaction`, timestamped commit with durable timestamp, rollback, stable/oldest timestamp advancement, checkpoint, and `reopen_conn`.

Control flow: it runs several scenarios in one test: prepare an insert; checkpoint; prepare updates that include existing and newly inserted keys; checkpoint; prepare removes over existing, updated, and newly inserted keys; commit baseline data; checkpoint and reopen; then prepare updates/removes over checkpointed keys. Each prepared transaction is either committed at the next timestamp or rolled back depending on scenario.

State and persistence behavior: the file stresses update-chain shapes that reconciliation may write to disk or history store. Reopen forces subsequent updates to be normal update chains rather than purely in-memory insert chains.

Dependencies and integration points: timestamp manager, checkpoint/reconciliation, history store, prepare commit/rollback resolution, and row/column key formats.

Risks: the test is mostly crash/error oriented and does not assert final values for every scenario; failures are expected as exceptions, reconciliation faults, or checkpoint/reopen issues.

Test signals: all prepare/commit/rollback/checkpoint/reopen phases complete without exceptions for both transaction endings and key formats.
