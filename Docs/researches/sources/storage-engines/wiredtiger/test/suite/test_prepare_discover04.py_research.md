# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover04.py

Purpose: verifies a prepared delete captured in a backup checkpoint can be discovered and resolved by either commit or rollback, then checkpointed after stable timestamp advancement.

Important APIs and types: `prepared_discover:`, `claim_prepared_id`, cursor `remove`, `commit_transaction` with durable timestamp, `rollback_transaction` with rollback timestamp, `make_scenarios` for commit and rollback endings.

Control flow: the test commits two baseline keys at timestamp 60, prepares deletes of both keys with prepared id 150 at timestamp 100, advances stable to 150, checkpoints, and backs up. In the reopened backup it walks `prepared_discover:`, claims the id, commits at 200/210 or rolls back at 200 according to the scenario, then advances stable to 220 and checkpoints.

State and persistence behavior: prepared tombstones are persisted through backup and then resolved in the copied database. The final checkpoint verifies the resolved prepared delete state can be made durable.

Dependencies and integration points: backup subsystem, timestamped deletes, prepare metadata, and checkpoint after resolution.

Risks: the test does not perform post-resolution reads, so its main failure surface is discovery/claim/checkpoint stability rather than logical value assertion. It still covers a historically risky prepared tombstone path.

Test signals: exactly one prepared id is discovered, resolution completes, stable timestamp can advance, and checkpoint finishes without error.
