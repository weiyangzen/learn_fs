<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower07.py

Purpose: confirms checkpoint cleanup does not run on a follower connection.

Important APIs/types/functions: class `test_layered_follower07` derives from `DisaggConfigMixin` and `test_cc_base`, uses `checkpoint_cleanup=[wait=1,file_wait_ms=0]`, `session.checkpoint('debug=(checkpoint_cleanup=true)')`, and statistic `stat.conn.checkpoint_cleanup_success`. It is skipped for the tiered hook.

Control flow: the follower creates and populates a small table via `test_cc_base.populate`, sleeps to let checkpoint cleanup run, forces a checkpoint with cleanup debug enabled, then opens `statistics:` and reads the cleanup-success counter.

State and persistence behavior: even though cleanup is configured and explicitly triggered, follower role should block checkpoint cleanup from running, preserving follower-disaggregated invariants.

Dependencies/integration points: integrates checkpoint cleanup server, follower role checks, and statistics. Risks include timing sensitivity from `sleep(1)` and stat semantics. Test signal is `checkpoint_cleanup_success == 0`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower07.py -->
