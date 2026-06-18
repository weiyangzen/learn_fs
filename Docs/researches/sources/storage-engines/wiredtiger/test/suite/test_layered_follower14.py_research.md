<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower14.py

Purpose: regression coverage for WT-16974, WT-16703, and WT-16798: sweep must not close layered or ingest dhandles on followers or during step-up when that would discard in-memory ingest/truncate state.

Important APIs/types/functions: `test_layered_follower14` derives from `sweep_util`, uses aggressive `file_manager` close settings, `verbose=(sweep:3)`, `wait_for_sweep`, `session.truncate`, role reconfigure to leader, direct ingest cursor pinning, and `wiredtiger.WT_NOTFOUND`.

Control flow: `test_layered_dhandle_not_swept_during_stepup` writes 1000 follower rows, pins the ingest file dhandle, waits several sweep cycles, steps up, and scans to ensure all rows remain. `test_layered_dhandle_not_swept_with_truncate_state` writes rows, commits a follower truncate 100-700 to create truncate-list state, waits for sweep, and scans to ensure only rows outside the range remain.

State and persistence behavior: in-memory ingest data and truncate-list entries attached to dhandles must survive sweep eligibility windows. Closing the wrong handle would create gaps or resurrect deleted ranges.

Dependencies/integration points: integrates sweep server timing, dhandle cache policy, follower role, step-up drain, and follower truncate visibility. Risks are timing (`timeout=120`) and verbose output coupling. Test signals are final scan counts and WT_NOTFOUND scan termination.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower14.py -->
