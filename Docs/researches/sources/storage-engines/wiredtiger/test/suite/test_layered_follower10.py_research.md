<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower10.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower10.py

Purpose: tests garbage collection of redundant follower ingest-table content after stable checkpoints are picked up, including inserts, tombstones, and open-cursor cases.

Important APIs/types/functions: uses `Oplog`, direct ingest URI `file:test_layered_follower10.wt_ingest`, helper `evict_ingest`, `count_ingest`, `disagg_advance_checkpoint`, and precise checkpoint config. `count_ingest` classifies values with length >2 as data and shorter values as tombstones.

Control flow: `setup` creates leader/follower tables. `test_gc_ingest_table` inserts data, advances checkpoint, proves open cursors prevent GC, closes them, advances another checkpoint, and expects ingest empty. `test_gc_ingest_table_with_remove` covers insert-then-remove chains and tombstones becoming removable only after a later stable checkpoint and cursor release. `test_gc_ingest_with_cursor` and `test_gc_ingest_with_no_open_cursor` cover first checkpoint pickup with and without pinned cursors.

State and persistence behavior: ingest records are pruned only when redundant with stable data and not pinned by open cursors; tombstones remain until deletes are represented in stable state.

Dependencies/integration points: integrates eviction-driven ingest GC, checkpoint prune timestamps, cursor pinning, and direct ingest inspection. Risks include value-length tombstone heuristic and heavy eviction loops. Test signals are exact `(data,tombstone)` counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower10.py -->
