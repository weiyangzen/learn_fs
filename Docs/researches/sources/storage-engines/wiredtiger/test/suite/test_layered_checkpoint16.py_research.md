# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint16.py

Purpose: verifies picking up a checkpoint that does not change table file metadata does not rewrite follower local file metadata, while a later data-changing checkpoint does.

Important APIs/types/functions: helper methods `insert_data`, `check_data`, `get_stat`, `assertStatEqual`, `assertStatGreater`; statistics `stat.conn.disagg_pick_up_file_meta_inserted` and `stat.conn.disagg_pick_up_file_meta_updated`; `disagg_advance_checkpoint`.

Control flow: the leader creates data at timestamp 10 and checkpoints. A follower opens and advances: data is checked, inserted stat must increase, updated stat remains zero. The leader advances stable timestamp to 15 and checkpoints without table changes; follower advances and should see same data with no new inserts or updates. Finally leader writes `v2-` data at timestamp 20, checkpoints, follower advances, data changes, inserts remain unchanged, and updated stat becomes greater than zero.

State and persistence behavior: separates metadata insertion for new follower files from metadata update for changed file metadata. Stable timestamp-only checkpoints should not cause file metadata churn.

Dependencies/integration points: follower checkpoint pickup diffing, file metadata stats, async stat propagation, and precise checkpoint behavior.

Risks: retry helpers account for asynchronous stats, but stat naming/semantics are part of the test contract. Data writes are full-table overwrites, not sparse updates.

Test signals: pass means idempotent/same-file metadata pickup avoids unnecessary metadata writes, and changed checkpoints still update metadata.
