# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover15.py

Purpose: ensures a follower-claimed prepared transaction that is rolled back and checkpointed does not resurface in a later `prepared_discover:` pass on the same checkpoint chain.

Important APIs and types: helper methods `_open_follower`, `_checkpoint`, `_discover_prepared_ids`, `prepared_discover:`, `claim_prepared_id`, `rollback_transaction`, and disaggregated role switches.

Control flow: the leader writes baseline values, prepares updates on several keys with id 17304, checkpoints while prepared, rolls back locally, and closes without checkpoint. The follower discovers and claims the id, rolls it back, steps up to leader, advances stable past rollback timestamp, checkpoints, steps back down to follower, and runs discover again.

State and persistence behavior: rollback resolution must be durable in the post-rollback checkpoint. Once rolled back, the prepared id should not be discoverable again from later checkpoint metadata.

Dependencies and integration points: prepared discovery lifecycle, follower claim rollback, checkpoint durability, role transition, and discover cursor empty/error handling.

Risks: `_discover_prepared_ids` treats an open error as empty, so the key signal is absence of the original id rather than distinction between no prepared content and unavailable cursor.

Test signals: initial discovery returns `[17304]`, and the later discovered id list does not contain `17304`.
