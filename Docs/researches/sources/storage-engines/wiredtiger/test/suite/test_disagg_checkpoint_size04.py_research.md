# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size04.py

Purpose: verifies disaggregated database-level size decreases when layered tables are dropped.

Important APIs and control flow: `get_database_size` parses `database_size` from complete checkpoint metadata. `test_drop_reduces_database_size` checkpoints an empty table, inserts 1000 large rows, checkpoints, drops the table, checkpoints again, and compares sizes. `test_drop_one_of_multiple_tables` inserts equal data into two tables, drops one, and verifies partial reclamation.

State and persistence: drop is queued and only reflected after the next checkpoint, matching WiredTiger metadata and checkpoint semantics.

Dependencies and integration: uses `@disagg_test_class`, layered URIs, `session.drop`, checkpoints, and disaggregated checkpoint metadata.

Risks and test signals: assertions allow metadata overhead slack but require substantial size reduction and surviving table accounting. Failures point at drop cleanup, free block accounting, or database-size metadata updates.
