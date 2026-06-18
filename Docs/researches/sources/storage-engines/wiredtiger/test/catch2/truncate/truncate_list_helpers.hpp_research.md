# Research: sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.hpp

## sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.hpp

Purpose: Header for shared layered truncate-list test utilities.

Important declarations: `truncate_range` alias, `make_item`, `as_view`, `truncate_list_head`, `truncate_list_size`, `lock_is_released`, `last_txn_op`, and class `truncate_list_fixture` with accessors for session, layered table, reference count, `add_entry`, and `commit_entry`.

Control flow/state: no implementation flow, but the public fixture contract exposes a mock-backed `WT_SESSION_IMPL`, an initialized `WT_LAYERED_TABLE`, and helper operations that manipulate `WT_TRUNCATE` entries and transaction commit state.

Dependencies/integration: includes Catch2, `wt_internal.h`, and `wrappers/mock_session.h`, binding tests to WiredTiger internals and mock sessions. It is included by truncate clear, GC, rollback, insert, visibility, visible-check, and write-conflict tests. Risks are broad coupling to private `WT_LAYERED_TABLE`, `WT_TRUNCATE`, and transaction op layouts. Test signals are indirect through the helpers' use in scenario files.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/truncate_list_helpers.hpp -->
