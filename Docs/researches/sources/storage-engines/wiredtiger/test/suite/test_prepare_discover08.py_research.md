# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover08.py

Purpose: ensures `prepared_discover:` can be the first cursor opened on a reopened layered-table connection, for both follower and leader reopen roles.

Important APIs and types: `role_scenarios`, `disagg_test_class`, `prepared_discover:`, `claim_prepared_id`, `reopen_conn`, `disagg_get_complete_checkpoint_meta`, and `prepared_id_str`.

Control flow: the leader commits baseline keys, prepares inserts for keys 4-6, advances stable, checkpoints, closes the table cursor, and reopens either as follower with checkpoint metadata or as leader. Without opening any data cursor first, it opens `prepared_discover:`, discovers id 123, claims and commits it at 200/210, and closes the cursor.

State and persistence behavior: discovery must initialize or access layered-table prepared metadata without relying on prior table cursor open side effects. Prepared inserts are committed in the reopened connection.

Dependencies and integration points: layered/disaggregated table open paths, discover cursor initialization, checkpoint metadata pickup, and role-specific connection open behavior.

Risks: this is a startup/order-of-operations regression test; future lazy-open changes to layered tables must keep discover cursor discovery independent of ordinary table cursor opens.

Test signals: the discovered id list is exactly `[123]`, and cursor close succeeds because all discovered prepared transactions were claimed and committed.
