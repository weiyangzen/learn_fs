# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_conflict.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_conflict.cpp

Purpose: Tests `WT_SESSION::drop` conflict paths that return `EBUSY` with specific sub-level errors and messages.

Important APIs/types: real connection/session wrappers, `prepare_session_and_error`, public cursor/drop APIs, lock macros `WT_WITH_CHECKPOINT_LOCK`, `WT_WITH_SCHEMA_LOCK`, `WT_WITH_TABLE_WRITE_LOCK`, and sub-level codes `WT_CONFLICT_BACKUP`, `WT_CONFLICT_DHANDLE`, `WT_CONFLICT_CHECKPOINT_LOCK`, `WT_CONFLICT_SCHEMA_LOCK`, `WT_CONFLICT_TABLE_LOCK`.

Control flow: first test creates a table and attempts drop while a backup cursor or table cursor remains open, covering simple tables, column-mapped tables, and POSIX tiered storage. Second test opens two sessions and attempts a lock-wait-zero drop while another session holds checkpoint, schema, or table write lock. Windows skips checkpoint/schema lock sections because spin lock behavior differs in same-thread tests.

State and persistence: creates/drop tables, cursors, optional tiered-storage home `WT_TEST`, and session error state. Cleanup closes cursors and drops tables after conflict checks.

Dependencies/integration: public schema/drop paths, backup cursor, tiered extension path, lock implementation, and test utility shell commands. Risks include platform-specific behavior, extension availability, and exact error messages. Test signals are `EBUSY` return plus exact `WT_ERROR_INFO`.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_drop_conflict.cpp -->
