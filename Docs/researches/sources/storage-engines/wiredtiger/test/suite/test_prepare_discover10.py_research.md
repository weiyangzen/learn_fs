# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover10.py

Purpose: tests that a prepared transaction reclaimed on a follower through `claim_prepared_id` survives step-up even though the reclaim session has no normal transaction id, and then resolves correctly after step-up.

Important APIs and types: properties `uri_b` and `_uris`, `multi_table` scenarios, disaggregated role reconfiguration, `prepared_discover:`, `claim_prepared_id`, `timestamp_transaction`, and checkpoint helpers.

Control flow: the leader creates one or two layered tables, commits baseline keys, prepares inserts for keys 4-6 with id 12345, checkpoints, rolls back the leader-side transaction, and closes without checkpoint. The follower discovers and claims the prepared id but keeps the claim live, steps up to leader, then commits or rolls back the claimed transaction. It checkpoints and reads both before and after resolution timestamps.

State and persistence behavior: step-up drain must match operations by prepared id rather than transaction id and patch operations onto the stable btree. Multi-table scenarios verify this logic across multiple layered tables.

Dependencies and integration points: disaggregated ingest drain, prepared id metadata, role step-up, layered-table timestamp visibility, and checkpointing after resolution.

Risks: this covers a narrow metadata matching path; failures can appear as successful discovery followed by missing or stale data after step-up.

Test signals: discovered id list is `[12345]`; keys 4-6 are absent at timestamp 60; at timestamp 220 they contain prepared values for commit resolution and are absent for rollback resolution.
