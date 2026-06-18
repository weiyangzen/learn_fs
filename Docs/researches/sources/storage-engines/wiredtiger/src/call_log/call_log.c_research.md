# sources/storage-engines/wiredtiger/src/call_log/call_log.c

## Purpose

Provides optional API call logging under `HAVE_CALL_LOG` for the timestamp simulator. It records selected connection/session timestamp and transaction API calls as JSON-like entries in a process-specific `wt_call_log` file so simulator tooling can replay or analyze API sequences.

## Important APIs, Types, And Functions

Lifecycle functions are `__wt_conn_call_log_setup` and `__wt_conn_call_log_teardown`. Shared formatting helpers are `__call_log_print_start`, `__call_log_print_input`, `__call_log_print_output`, and exported `__wt_call_log_print_return`. API-specific loggers include `__wt_call_log_open_session`, `__wt_call_log_set_timestamp`, `__wt_call_log_query_timestamp`, `__wt_call_log_begin_transaction`, `__wt_call_log_prepare_transaction`, `__wt_call_log_commit_transaction`, `__wt_call_log_rollback_transaction`, `__wt_call_log_timestamp_transaction`, `__wt_call_log_timestamp_transaction_uint`, `__wt_call_log_prepared_id_transaction`, `__wt_call_log_prepared_id_transaction_uint`, and `__wt_call_log_close_session`.

The file uses `WT_CONNECTION_IMPL::call_log_fst`, `WT_CONN_CALL_LOG_ENABLED`, session/connection pointer values as IDs, `WT_TS_TXN_TYPE`, WiredTiger file-system stream APIs, and variadic formatting helpers.

## Control Flow

Setup skips readonly connections, builds a filename containing the process ID, opens it for append/create, and sets the enabled flag. Every logger first checks the enabled flag, prints a class/method header, prints a connection or session ID when needed, prints an input object from preformatted JSON fragments, prints an output object, and finally writes a return object with return value and error string. Query timestamp logs output only on successful API return to avoid recording garbage. `timestamp_transaction_uint` maps `WT_TS_TXN_TYPE_*` enum values to symbolic strings. Teardown closes the file stream when enabled.

## State And Persistence Behavior

The persistent artifact is an append-only call-log file in the connection home context. It is not WiredTiger database state and is not intended for recovery. The file stores pointer values as session/connection identifiers for simulator mapping, configuration strings copied from API calls, timestamp/prepared-id values, return codes, and optional error strings. Close-session logging intentionally has no return section in this file, unlike most other entries.

## Dependencies And Integration Points

Integrated into public API paths through conditional call-log hooks and compiled only when `HAVE_CALL_LOG` is defined. It depends on WiredTiger scratch buffers, filename construction, filesystem open/close, formatted stream output, connection flags, and simulator-side expectations for `class_name`, `method_name`, `session_id`, `connection_id`, `input`, `output`, and `return` fields.

## Risks

The output is assembled with fixed 128-byte buffers for config fragments, so long config strings can fail formatting or truncate depending on `__wt_snprintf` semantics. Raw config strings are inserted into JSON without escaping, so embedded quotes or control characters can produce invalid JSON. There is no explicit synchronization around writes; concurrent API calls may interleave unless higher layers serialize or the stream implementation protects writes. Pointer IDs are process-local and not stable across runs. The close-session entry omits a return block, which consumers must tolerate.

## Test Signals

Tests should compile with `HAVE_CALL_LOG`, verify readonly setup does not create/enable logging, exercise each API logger, parse or pattern-check emitted entries, validate query timestamp omits output on failure, confirm enum-to-string mapping for timestamp types, and stress concurrent sessions for malformed/interleaved records. Simulator tests under `test/simulator/timestamp/call_log_manager` are a natural integration signal.
