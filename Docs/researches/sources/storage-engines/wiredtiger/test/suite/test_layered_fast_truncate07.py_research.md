<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate07.py

Purpose: verifies that follower-initiated range truncate resolves NULL start/stop cursors to concrete first/last visible keys and logs the bounded truncate list entry.

Important APIs/types/functions: class `test_layered_fast_truncate07` uses verbose config `verbose=[layered:3]`, `captureout.checkAdditionalPattern`, `cleanStdout`, local `insert_range`, `follower_visible_keys`, `expected_keys`, and `assert_trunc_log`. Scenarios cover string and integer key formats.

Control flow: `setup_follower` creates a layered table, inserts keys 1-100 on the leader, checkpoints, and reopens as follower with checkpoint metadata and layered verbose logging. Tests cover bounded ranges, null start, null stop, both null, open-ended truncates followed by appends, and overlaps where a second open-ended truncate must search-near past already-deleted keys before logging a concrete range.

State and persistence behavior: open-ended API calls are normalized into bounded entries in the follower truncate list. Later appends after an open-ended truncate remain visible.

Dependencies/integration points: relies on verbose log string shape, disaggregated checkpoint metadata, key string formatting, and cursor search-near behavior during overlap resolution. Risks include fragile log-pattern coupling. Test signals are log entries and exact forward/backward visible keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate07.py -->
