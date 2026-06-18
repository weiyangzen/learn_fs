# Research: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_rollback.cpp

## sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_rollback.cpp

Purpose: Unit tests for rollback of follower truncate transaction operations through `__wti_layered_table_truncate_rollback`.

Important helpers/APIs: `make_op` creates a `WT_TXN_OP` of type `WT_TXN_OP_FOLLOWER_TRUNCATE`; `rollback_truncate` calls the rollback helper. Uses fixture queue helpers and reference-count/lock checks.

Control flow: scenarios verify rollback removes a single entry from the list, clears the op pointer, releases the dhandle reference when the list becomes empty, releases the truncate lock, and in a three-entry list removes only the targeted middle entry while preserving order and leaving other operation pointers and reference count unchanged.

State and persistence: in-memory truncate queue, transaction op pointer, and table reference count. No disk state.

Dependencies/integration: verifies transaction rollback cleanup for layered truncate list entries. Risks include dangling op pointers, removing wrong queue node, reference underflow on non-empty lists, and lock leaks. Test signals are list size/order, op pointer nulling, reference counts, and lock acquisition after rollback.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_layered_table_truncate_rollback.cpp -->
