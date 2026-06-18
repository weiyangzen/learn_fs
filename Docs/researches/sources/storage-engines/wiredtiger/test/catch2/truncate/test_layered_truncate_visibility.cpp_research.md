# Research: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_truncate_visibility.cpp

## sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_truncate_visibility.cpp

Purpose: Detailed unit tests for follower layered-table truncate visibility, centered on `__wt_truncate_delete_visible_check`, commit apply, and rollback apply behavior.

Important fixture/APIs: `layered_truncate_visibility_fixture` builds a mock session, transaction shared list, `WT_TXN`, and `WT_LAYERED_TABLE` with truncate queue/lock. Helpers set reader snapshot state, set committer time point, add truncate entries with copied keys, and call visibility check.

Control flow: tests cover own uncommitted truncate visible, other uncommitted truncate invisible, committed truncate gated by read timestamp, overlapping ranges with different timestamps, commit stamping through `__wti_mark_committed_truncate_table_apply`, durable timestamp and snapshot-window visibility, overlap precedence when a newly committed range becomes visible, and rollback removal through `__wti_layered_table_truncate_rollback_apply`.

State and persistence: all state is mock in-memory: txn snapshot min/max, shared read timestamp, truncate txn id, start/durable timestamps, committed flag, copied keys, queue links, and references.

Dependencies/integration: touches internal transaction visibility semantics, layered table queue traversal, key-copy outputs, and rollback/commit apply callbacks. Risks include subtle precedence rules for overlapping ranges and exact snapshot-window fabrication. Test signals are return codes, matched start/stop buffers, timestamp fields, committed flag, queue order, and op pointer clearing.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_truncate_visibility.cpp -->
