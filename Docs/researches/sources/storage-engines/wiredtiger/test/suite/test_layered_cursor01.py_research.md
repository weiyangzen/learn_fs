# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor01.py

Purpose: broad cursor operation regression suite for layered tables over leader and follower, covering scan order and positioning after inserts, updates, removes, checkpoints, and follower checkpoint advance.

Important APIs/types/functions: uses `Oplog` helper from `helper_disagg`, position helpers for `search`, `search_near`, `next`, and `prev`, scenarios over those positioning functions, `setup_follower`, `create_table`, `oplog_apply_traffic`, `check_cursor_ops`, `checkpoint_and_advance`, and cursor `next`/`prev` traversal.

Control flow: setup opens a follower connection and creates matching leader/follower layered tables. The Oplog applies batches of inserts plus optional updates/removes to both sessions and maintains an expected table snapshot. `check_cursor_ops` sorts expected keys lexicographically, scans forward/backward on both leader and follower, and verifies positioning at start/quarter/mid/three-quarter/end followed by forward and backward iteration. Test variants run empty tables, populated tables, update percentages, remove percentages, combined update/remove cases, and offset cases.

State and persistence behavior: state is mirrored between leader and follower local tables via Oplog operations and then through leader checkpoint/follower advance. Expected state is maintained in Oplog rather than by reading back from one side.

Dependencies/integration points: layered cursor search/iteration, follower checkpoint pickup, Oplog helper semantics, and disaggregated storage scenarios.

Risks: two test method names for `test_populated_tables_with_updates_20_percent` appear, so the later definition overrides the earlier in Python. Also some offset attributes use `updates_offset` while helper reads `update_offset`, reducing intended offset coverage.

Test signals: pass means cursor positioning and bidirectional scans match expected logical table content before and after checkpoint pickup.
