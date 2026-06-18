# sources/sync-backup/rsync/testsuite/daemon-delete-stats_test.py

Purpose: verifies daemon upload delete itemization and, for protocol >= 31, delete statistics.

Important APIs/types/functions: `build_rsyncd_conf`, `forced_protocol`, `start_test_daemon`, `rsync_argv('-a', '--delete', '-i', '--stats')`, and output substring checks.

Control flow: create source with `keep.txt` and destination with matching keep plus extra `delete.txt`, start daemon, upload with delete/itemize/stats, require success, require `*deleting   delete.txt`, and require `Number of deleted files: 1 (reg: 1)` unless protocol is pinned below 31.

State and persistence behavior: daemon destination loses one file; stdout/stderr is also an asserted protocol signal.

Dependencies and integration points: daemon receiver delete reporting, itemize output, stats message `NDX_DEL_STATS`, and protocol gating.

Risks and test signals: older forced protocols cannot receive the delete-stats count. Failures distinguish missing itemization from missing stats.
