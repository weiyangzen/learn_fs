<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate17.py

Purpose: confirms step-up replay of follower truncates uses page-level fast truncate (`WT_REF_DELETED`) rather than only per-key deletes.

Important APIs/types/functions: uses `wiredtiger.stat`, `stat.conn.rec_page_delete_fast`, `LayeredFastTruncateConfigMixin`, `open_follower`, `leader_checkpoint`, `search_at`, and local `assert_fast_truncate_fired` and `assert_ranges_deleted`. The table uses `leaf_page_max=4096` and 5000 rows to make interior pages eligible.

Control flow: setup creates the leader table, writes all rows at ts=10, checkpoints, and opens a follower. Tests create one large interior truncate or three disjoint ranges on the follower, record the fast-delete statistic, step up, assert the statistic increased, and then scan/search all keys at ts=30 for expected deletion.

State and persistence behavior: pending follower truncate ranges become stable deleted-page state during role promotion. Boundary pages are left outside the range to make fast-delete eligibility clear.

Dependencies/integration points: integrates follower step-up drain with WiredTiger reconciliation fast-delete counters. Risks include test sensitivity to page layout or stat semantics. Test signals are counter increase and full key-space visibility validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate17.py -->
