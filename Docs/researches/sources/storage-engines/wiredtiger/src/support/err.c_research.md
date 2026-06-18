# sources/storage-engines/wiredtiger/src/support/err.c

## Purpose
Implements WiredTiger event/error/message/progress reporting, default event handlers, verbose formatting, panic handling, extension message APIs, object-type error helpers, and a thread-local recent-error ring used for diagnostics.

## Important APIs, Types, and Functions
- `__wt_event_handler_set` installs defaults for null event-handler methods.
- `__eventv` is the central formatter for errors and verbose messages, supporting plain text and JSON output, prefixes, dhandle/session names, timestamps, thread IDs, categories, levels, log IDs, dynamic scratch buffers, and fallback to stderr.
- Public wrappers include `__wt_err_func`, `__wt_errx_func_id`, `__wt_errx_func`, `__wt_panic_func`, `__wt_verbose_worker_id`, `__wt_verbose_worker`, `__wt_msg`, `__wt_progress`, and extension APIs.
- `__wt_inmem_unsupported_op`, `__wt_object_unsupported`, `__wt_bad_object_type`, and `__wt_unexpected_object_type` centralize common API errors.
- `__wt_error_log_add`, `wiredtiger_dump_error_log`, `__wt_error_log_dump_recent`, and `__wt_error_log_to_handler` manage a thread-local circular error log.

## Control Flow
Default handlers write errors to stderr, messages to stdout, and ignore progress/close/general events. `__eventv` handles null sessions by writing to stderr, otherwise formats into a stack buffer first, grows scratch buffers for long messages, optionally JSON-encodes the message string, appends error strings without duplicating existing suffixes, calls the configured handler, and reports handler failures through `__handler_failure`. Panic first dumps the recent error log, reports the panic and restart message, optionally aborts in diagnostic corruption settings, then sets the connection panic flag.

The error log is thread-local. Add records only nonzero errors, stores file/function/line/expression/error/suberror in a ring, and dump paths either call a user callback or send recent entries through the event handler before clearing when appropriate.

## State and Persistence Behavior
No durable database state is written. Runtime state includes session event-handler pointers, connection JSON-output/error-prefix flags, thread-local error-log rings, and connection panic/data-corruption flags. Output may go to application callbacks, stdout/stderr, or extension-provided handlers.

## Dependencies and Integration Points
Used throughout WiredTiger through error macros, verbose macros, extension API, session helper last-error paths, and panic/assertion paths. Depends on scratch buffers, JSON string encoding, thread ID/time helpers, verbose category tables, event handler ABI, connection/session flags, and error string mapping.

## Risks
Error paths must avoid recursion, allocation failure crashes, and varargs misuse. JSON formatting must correctly escape user messages. Event-handler failure handling must not call a failing handler indefinitely. Panic ordering is important: applications should see the original failing thread before every API call starts returning panic. Thread-local logs help diagnostics but can miss cross-thread context.

## Test Signals
Coverage should include default handler output, application handler failure fallback, JSON/plain formatting, long message allocation, duplicate error-string suppression, null-session stderr fallback, panic flag behavior, diagnostic abort configurations, extension error/message APIs, object-type errors, error-log ring wraparound, dump-and-clear semantics, and recent-dump without clear.
