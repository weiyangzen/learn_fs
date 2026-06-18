# sources/storage-engines/wiredtiger/test/model/test/common/wiredtiger_util.cpp

Purpose: implements WT test wrappers declared in `wiredtiger_util.h`, giving model tests concise WT operations with consistent timestamp, transaction, checkpoint, and debug-log behavior.

Important APIs and functions: `wt_get`, `wt_insert`, `wt_remove`, `wt_truncate`, `wt_update`, `wt_txn_begin`, `wt_txn_commit`, `wt_txn_prepare`, `wt_txn_reset_snapshot`, `wt_txn_rollback`, `wt_txn_set_commit_timestamp`, `wt_txn_get`, `wt_txn_insert`, `wt_txn_remove`, `wt_ckpt_get`, `wt_ckpt_create`, `wt_get_timestamp`, `wt_set_timestamp`, and `wt_print_debug_log`.

Control flow: simple operations begin a WT transaction, open cursors, set key/value via model helpers, execute cursor calls, tolerate expected return codes (`WT_NOTFOUND`, `WT_DUPLICATE_KEY`, `WT_PREPARE_CONFLICT`, `WT_ROLLBACK` depending on operation), close cursors, and commit or rollback with timestamp configs. Transaction helpers operate on an already active session transaction. Checkpoint reads open checkpoint cursors with optional debug read timestamp. Debug log printing opens a session, obtains the first LSN from WT internals, and calls `__wt_txn_printlog`.

State and persistence: mutates WT tables and connection timestamps. Checkpoints and debug logs are WT persistent artifacts. `wt_print_debug_log` reads internal WT connection state and writes a JSON/debug log file.

Dependencies and integration: includes `wiredtiger.h`, C `test_util.h`, WT log private header, `model/test/wiredtiger_util.h`, and `model/util.h`. Used by paired model/WT test macros and debug-log verification.

Risks: many config strings use 64-byte buffers; large timestamp formatting is safe for hex `uint64_t` but adding options could overflow if not resized. Some wrappers commit even after operation-level WT errors unless handled specially; truncate rolls back on `WT_ROLLBACK`. Direct use of WT internals (`WT_CONNECTION_IMPL`, `__wt_txn_printlog`) is version-sensitive.

Test signals: every paired macro depends on these wrappers. Failures show as unexpected `testutil_check` aborts, mismatched return codes, mismatched read values, timestamp mismatch, or inability to print debug logs.
