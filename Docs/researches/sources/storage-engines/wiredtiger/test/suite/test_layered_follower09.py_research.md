<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower09.py

Purpose: tests pinning of ingest table content by an active read transaction while data becomes obsolete and checkpoints advance.

Important APIs/types/functions: uses `Oplog`, `disagg_advance_checkpoint`, `debug=(release_evict)` cursor on `file:test_layered_follower09.wt_ingest`, large cache config, and timestamped read transactions.

Control flow: leader and follower create matching layered tables. An oplog inserts 20000 rows on both. A second follower session starts a read transaction at the insert timestamp and opens a cursor, pinning the ingest content. The oplog then removes all rows on leader and follower, leader advances oldest/stable and checkpoints, follower advances checkpoint, and eviction is triggered across ingest keys. The pinned cursor continues scanning and must still see all original rows.

State and persistence behavior: active readers pin older ingest versions even after those records are deleted, made obsolete, and checkpoint state advances.

Dependencies/integration points: integrates oplog helper, ingest file eviction, timestamped reads, checkpoint pickup, and obsolete cleanup. Risks are heavy row count and eviction loop cost. Test signal is final cursor count equal to `nitems`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower09.py -->
