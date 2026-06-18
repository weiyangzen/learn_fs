# sources/storage-engines/wiredtiger/src/schema/schema_util.c

## Purpose
Provides shared schema utility routines for backup conflict checks, data-source lookup, internal schema sessions, namespace validation, simple-table detection, and a debug crash hook used by schema operations.

## Important APIs, Types, and Functions
- `__wti_schema_backup_check(session, name)` rejects schema operations that would conflict with an active hot backup file list.
- `__wt_schema_get_source(session, name)` scans `S2C(session)->dsrcqh` for a matching registered data-source prefix.
- `__wti_schema_internal_session` opens an internal metadata-capable schema session when the caller has a running transaction, preventing schema records from being buffered in the user's transaction.
- `__wti_schema_session_release` closes that internal session and propagates saved error information back to the original session.
- `__wt_str_name_check` and `__wt_name_check` protect the `WiredTiger` namespace and reject JSON/config grouping characters in object names.
- `__wt_is_simple_table` detects unnamed-column table configs.
- `__wti_debug_crash_if_flag_set` simulates crash points when configured debug flags are set.

## Control Flow
Backup checks first do a cheap atomic read of `conn->backup.start`, then take the hot-backup read lock only when needed and compare the target name against the active backup list. Internal schema session handling returns the current session unless a transaction is running; release mirrors that decision. Name validation peels URI/table prefixes before checking reserved names and disallowed characters.

## State and Persistence Behavior
The file does not persist metadata directly, but it protects persistence boundaries. Backup checking prevents destructive schema changes to files being backed up. Internal schema sessions isolate schema metadata operations from application transactions. Debug crash support intentionally sleeps before aborting to let previous metadata changes reach stable storage in targeted test scenarios.

## Dependencies and Integration Points
Integrated into create/drop/alter/rename/truncate and other schema paths. It depends on connection backup state, hot-backup locks, connection data-source queues, session open/close support, transaction flags, config parsing, and error propagation helpers.

## Risks
Namespace validation must stay aligned with metadata/config parser constraints; relaxing it can expose metadata corruption paths. Internal-session error propagation must preserve the first meaningful user-visible error. Backup conflict checks rely on lock ordering and the backup list lifecycle; races here could allow file removal while a backup cursor still expects the file.

## Test Signals
Look for hot-backup/drop conflict tests, schema operations inside active transactions, object-name validation tests for `WiredTiger` and punctuation-heavy names, extension data-source dispatch tests, simple-table config tests, and debug crash/failpoint coverage around schema metadata persistence.
