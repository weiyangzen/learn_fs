<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate21.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate21.py

Purpose: regression test for parent reconciliation after instantiated fast-truncate leaves become globally visible; parent images must be rebuilt as full base images rather than unsafe deltas referencing freed leaf blocks.

Important APIs/types/functions: uses direct `wttest.WiredTigerTestCase`, page-delta config, `wiredtiger.stat`, tiny page sizing, `debug=(release_evict)`, `reopen_disagg_conn`, timestamp management, and `session.verify`.

Control flow: setup inserts 200 rows, checkpoints, evicts leaves, and reopens so internal pages have valid disaggregated page ids. It fast-truncates 50-150 at ts=20 and checkpoints while oldest remains low, so proxy cells remain. It then reads inside the truncated range at ts=10 to instantiate fully covered leaves, advances oldest/stable to 30, updates only boundary leaves at ts=35 to encourage parent delta mode, checkpoints, and verifies the table.

State and persistence behavior: tracks deleted leaf instantiation, global visibility, proxy-cell removal, block freeing, and parent reconciliation. The correctness signal is that verify passes after the potentially dangerous state transition.

Dependencies/integration points: relies on fast-delete eligibility, page-delta machinery, oldest timestamp advancement, and verify catching stale block references. Risks are page layout sensitivity. Test signals are fast-delete and read-deleted stat increases followed by successful `session.verify`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate21.py -->
