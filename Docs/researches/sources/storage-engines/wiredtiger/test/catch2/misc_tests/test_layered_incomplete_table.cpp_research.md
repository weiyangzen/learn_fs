# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_layered_incomplete_table.cpp

## Purpose
Tests recovery/open behavior for incomplete layered-table metadata in disaggregated storage, covering leader/follower roles and missing ingest/stable file metadata entries.

## Important APIs, Types, And Functions
`build_cfg` builds wiredtiger_open config with palite page-log extension and disaggregated role. `prepare_db` creates a complete layered table, then optionally removes `file:<table>.wt_ingest` and/or `file:<table>.wt_stable` metadata via `__wt_metadata_remove`. `try_reopen` calls `wiredtiger_open`; `reopen_aborts` forks a child and detects abort/nonzero exit.

## Control Flow
On non-Windows builds, tests prepare a home directory for each scenario, reopen as leader or follower, and assert success or abort. Leader requires both ingest and stable entries. Follower requires ingest but allows missing stable. Abort cases are isolated in child processes so `WT_ASSERT_ALWAYS` does not kill the Catch2 runner.

## State And Persistence Behavior
This test creates real WiredTiger homes and persists metadata changes across close/reopen. Metadata surgery is done in a follower connection before data handles are opened, avoiding active-handle close panics.

## Dependencies And Integration Points
Depends on Unix `fork/wait/signal`, `connection_wrapper`, test utilities, palite page-log extension path, disaggregated storage config, layered table metadata, and `__metadata_clean_incomplete_table` behavior.

## Risks And Edge Cases
Risks include role-specific requirements drifting, metadata removal while handles are active, Catch2 signal handlers interfering with abort detection, and platform incompatibility; the file is disabled on Windows.

## Test Signals
Successful reopens must return zero; invalid metadata combinations must abort or exit nonzero in the child. Homes are cleaned after each section.
