<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower13.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower13.py

Purpose: verifies ingest garbage collection removes associated on-disk values when keys are pruned during eviction.

Important APIs/types/functions: uses direct ingest URI `file:test_layered_follower13.wt_ingest`, `stat.dsrc.rec_ingest_garbage_collection_keys_update_chain`, debug eviction sessions, direct ingest cursor checks, and disaggregated checkpoint advancement.

Control flow: each test creates matching leader/follower layered tables, mirrors an insert at ts=10 to the follower, evicts it to create an on-disk ingest image, applies another operation, checkpoints/advances, evicts again, and checks the ingest btree. The scenarios are: update at ts=20, delete at ts=20, and a no-timestamp/global-visible tombstone placed directly in the ingest btree while the original insert is not prunable.

State and persistence behavior: GC must clear both update chains and any on-disk value image, often by writing a tombstone, so direct ingest searches no longer find the key. The statistic should report one garbage-collected update-chain key.

Dependencies/integration points: integrates eviction reconciliation, direct ingest btree operations, checkpoint pickup, no-timestamp deletes, and per-dsrc stats. Risks include stat counter exactness and direct file URI coupling. Test signals are WT_NOTFOUND in ingest and stat value `1`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower13.py -->
