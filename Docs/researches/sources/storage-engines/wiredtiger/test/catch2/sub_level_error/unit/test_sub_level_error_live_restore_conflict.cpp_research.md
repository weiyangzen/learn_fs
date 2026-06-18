# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_live_restore_conflict.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_live_restore_conflict.cpp

Purpose: Tests live-restore conflict reporting for backup cursor creation.

Important APIs/types: `utils::live_restore_test_env` supplies a live-restore-enabled connection, `prepare_session_and_error` opens a session and exposes `WT_ERROR_INFO`, and `session->open_cursor("backup:")` is expected to fail with `EINVAL`.

Control flow: within the section, the test prepares a session from the live-restore environment, attempts to open a backup cursor, asserts the cursor remains `NULL`, and checks `WT_CONFLICT_LIVE_RESTORE` with message "backup cannot be taken when live restore is enabled".

State and persistence: the live-restore environment owns the connection/home setup. The test mutates only session error state and a cursor output pointer.

Dependencies/integration: integrates live restore test environment, public backup cursor path, and sub-level error storage. Risks are dependency on live_restore fixture setup and exact message text. Test signals are `EINVAL`, null cursor, and exact error info.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_live_restore_conflict.cpp -->
