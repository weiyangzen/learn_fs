<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower02.py

Purpose: tests leader/follower disaggregated operation with oplog-style replicated writes and repeated checkpoint pickup.

Important APIs/types/functions: uses `helper_disagg.Oplog`, `WiredTigerCursor`, `statistic_uri`, connection statistics `checkpoints_total_succeed` and `layered_table_manager_checkpoints_disagg_pick_up_follower`, plus `disagg_advance_checkpoint`.

Control flow: the leader creates a layered table and an `Oplog` stream. A follower connection creates the same table. The test applies insert/update traffic to the leader, checkpoints, applies a prefix of operations to the follower, advances checkpoint, and validates follower contents. A loop repeats checkpoint creation, optional new leader traffic, follower catch-up to at least checkpoint position, checkpoint pickup, and full checks.

State and persistence behavior: leader stable checkpoints coexist with follower-applied ingest operations. Checkpoint pickup should add stable content without losing or double-applying follower-local oplog progress.

Dependencies/integration points: integrates helper oplog generation, statistics logging, disaggregated checkpoint manager, and layered table reads. Risks include quadratic checking from position 0 and dependence on exact statistic counts. Test signals are oplog consistency checks and checkpoint/pickup statistic equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower02.py -->
