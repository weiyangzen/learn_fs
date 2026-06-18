# sources/storage-engines/wiredtiger/test/suite/test_debug_mode04.py

Purpose: simple coverage for `debug_mode=(eviction=true)`, ensuring forced debug eviction mode does not break normal file-table writes and checkpoints.

Important APIs and control flow: `add_data` creates `file:test_debug`, opens a cursor, inserts a set of key/value pairs, closes it, and checkpoints. One test runs with eviction debug mode enabled from `conn_config`; another disables it with `conn.reconfigure('debug_mode=(eviction=false)')` before doing the same workload.

State and persistence: table data is persisted through a checkpoint. The expected behavior is absence of errors rather than a statistic assertion.

Dependencies and integration: uses `wttest`, session create/open cursor/checkpoint, and connection reconfiguration.

Risks and test signals: this is mostly a stability guard. It catches crashes, assertion failures, or configuration plumbing regressions in the debug eviction path but does not prove a specific eviction policy was exercised.
