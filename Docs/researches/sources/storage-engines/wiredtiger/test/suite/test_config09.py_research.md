<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config09.py

Purpose: tests hash bucket configuration and checkpoint dirty-handle skipping statistics.

Important APIs and control flow: `conn_config` sets `hash=(buckets=256,dhandle_buckets=1024),statistics=(fast)`. Helpers create 50 small tables, update half of them, checkpoint, and read connection stats. `test_config09_invalid()` rejects non-power-of-two bucket values. `test_config09()` verifies configured bucket stats, then asserts checkpoint applied handles are around half the table count, skipped handles are nonzero, and selected per-checkpoint stats reset rather than accumulate.

State, persistence, and dependencies: persistent state is many small tables with checkpointed clean/dirty states. Dependencies are `wiredtiger.stat`, statistics cursors, checkpoint internals, and hash configuration parsing. Tiered storage is skipped.

Integration points: exercises dhandle hash sizing and checkpoint optimization that avoids clean handles.

Risks and test signals: internal tables make exact counts impossible, so the test uses ranges. Failures point to hash validation, stats publication, dirty-table detection, or stat reset regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config09.py -->
