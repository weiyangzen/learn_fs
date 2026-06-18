<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower03.py

Purpose: verifies historical reads after reopening or restarting without local files in disaggregated/layered configurations.

Important APIs/types/functions: uses `restart_without_local_files`, `disagg_get_complete_checkpoint_meta`, `reopen_conn`, `conn.reconfigure`, timestamped transactions, and scenarios for `layered:` URI, table-layered disagg, and shared table disagg without logging.

Control flow: a node starts as follower, steps up to leader, creates a table, writes 500 rows at timestamp 100, checkpoints, updates all rows at timestamp 200, sets oldest/stable timestamps, and checkpoints again. It verifies reads at both timestamps, then reopens while keeping local files and reconfigures checkpoint metadata/leader role. Finally it restarts without local files and again verifies reads at both timestamps.

State and persistence behavior: tests that stable checkpoint and history-store content are available after local-file loss and role changes, preserving older values at timestamp 100 and newer values at 200.

Dependencies/integration points: uses precise checkpoints, checkpoint metadata, history store, role reconfiguration, and helper restart mechanics. Risks include precise-checkpoint timestamp requirements. Test signals are exact per-key values under timestamped reads after both restart paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower03.py -->
