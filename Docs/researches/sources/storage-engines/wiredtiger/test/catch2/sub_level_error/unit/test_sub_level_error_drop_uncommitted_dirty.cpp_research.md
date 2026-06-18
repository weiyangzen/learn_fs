# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_uncommitted_dirty.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_uncommitted_dirty.cpp

Purpose: Tests dhandle-close/drop conflict sub-level errors for uncommitted or dirty table data.

Important APIs/types: `__wt_session_get_dhandle`, `__wt_conn_dhandle_close`, `__wt_session_release_dhandle`, `S2BT(session_impl)`, dhandle flag `WT_DHANDLE_IS_METADATA`, btree flag `WT_BTREE_BULK`, `WT_SESSION_LOCKED_SCHEMA`, and sub-level codes `WT_UNCOMMITTED_DATA` and `WT_DIRTY_DATA`.

Control flow: after creating a table and acquiring its file dhandle, sections vary visibility-check flag, `max_upd_txn`, schema lock, btree `modified`, bulk mode, and metadata handle flags. The expected EBUSY cases are only: visibility-check enabled with uncommitted txn state, and schema-locked close of a modified non-bulk non-metadata btree.

State and persistence: mutates internal btree/dhandle fields and session lock flags. At the end it resets `max_upd_txn`, `modified`, bulk and metadata flags, releases dhandle, and drops the table.

Dependencies/integration: tightly coupled to dhandle close logic and btree dirty/uncommitted checks. Risks include manual internal field manipulation and need for precise cleanup to avoid drop failures. Test signals are return codes and exact error-info triples.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_uncommitted_dirty.cpp -->
