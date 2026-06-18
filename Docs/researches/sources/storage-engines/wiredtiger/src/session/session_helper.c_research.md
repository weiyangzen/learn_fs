# sources/storage-engines/wiredtiger/src/session/session_helper.c

## Purpose
Provides session-array walking, diagnostic session dumping, and helpers for per-session last-error storage used by the public `WT_SESSION::get_last_error` API.

## Important APIs, Types, and Functions
- `__wt_session_array_walk(session, walk_func, skip_internal, cookiep)` iterates active sessions and calls a callback with early-exit support.
- `__wt_session_dump(session, dump_session, show_cursors)` emits diagnostic details about a session, transaction state, and optionally cursors.
- `__wt_session_reset_last_error` resets `WT_ERROR_INFO` to success/none defaults.
- `__wt_session_set_last_error` records the first error, sub-level error, and formatted message for an API call.

## Control Flow
Session-array walk reads the session count once, then acquire-reads each slot's `active` flag, pairing with session open's release publish. It skips inactive and optionally internal sessions, asserts hazard memory exists, invokes the callback, and honors callback-requested early exit. Dumping formats fields through `__wt_msg` and uses scratch buffers for cursor flag text. Last-error setting returns if saving is disabled, the session is null, or an error is already saved.

## State and Persistence Behavior
No durable state is written. The file reads volatile session-array state safely, exposes diagnostic state through event handlers, and maintains per-session `err_info` fields plus the backing formatted-message buffer. The first-error-wins rule preserves the initial failure from an API call.

## Dependencies and Integration Points
Used by generation draining, diagnostics, verbose transaction dumps, session API error retrieval, and API macros that reset/save errors. Depends on connection session arrays, session active publication barriers, event messaging, scratch buffers, cursor queues, transaction verbose dump, and error validation helpers.

## Risks
Callbacks must tolerate sessions changing while the array is walked. Missing acquire/release pairing could expose partially initialized session slots. Last-error formatting must not overwrite an earlier error and must only run with valid sub-level error codes. Diagnostic dumping can recurse into event handlers and should avoid destabilizing already-failing paths.

## Test Signals
Relevant tests include session-array walk under concurrent open/close, skip-internal behavior, early-exit callbacks, diagnostic dump output with and without cursors, `get_last_error` first-error semantics, empty-message handling, and internal session error propagation from schema helpers.
