# sources/storage-engines/wiredtiger/test/suite/test_disagg_util01.py

Purpose: validates automatic pickup of latest disaggregated checkpoints in library leader mode and through the `wt` utility in follower mode.

Important APIs and control flow: `test_leader_auto_pickup` writes rows as leader, checkpoints, steps down to follower, restarts without local files as leader, verifies rows, and checkpoints new writes. `_run_wt_as_follower` closes the leader, creates a follower home symlinked to `kv_home`, loads the page-log extension path, and runs `wt` with follower config. Other tests check `wt list`, no-checkpoint stderr, and latest-checkpoint dump content.

State and persistence: checkpoint metadata and page-log contents are shared across leader/follower homes; local files are intentionally removed or separate.

Dependencies and integration: uses `@disagg_test_class`, `suite_subprocess`, `wt_builddir`, page-log extension discovery, symlinks, and utility output.

Risks and test signals: checks row visibility, `layered:` listing, `no complete checkpoint found`, and absence of old values. Failures indicate pickup or utility follower regressions.
