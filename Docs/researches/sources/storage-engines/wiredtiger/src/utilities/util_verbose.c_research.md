<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_verbose.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_verbose.c

Purpose: Provides the verbose `WT_EVENT_HANDLER` used by the utility to surface WiredTiger errors, messages, and progress updates.

Important APIs/functions: `__handle_error_verbose` writes errors to stderr; `__handle_message_verbose` writes messages to stdout; `__handle_progress_verbose` prints carriage-return progress with operation name and count. `__event_handler_verbose` wires these callbacks into a `WT_EVENT_HANDLER`, exposed as global `verbose_handler`.

Control flow: Each callback ignores unused handler/session fields and returns `EIO` when its printf/fprintf operation fails, otherwise `0`. Progress output uses `\r` rather than newline so callers such as salvage and verify add a newline after successful verbose runs.

State and persistence behavior: No database persistence. It affects process output and can influence WiredTiger callback return handling if writes to stdout/stderr fail.

Dependencies and integration points: Uses WiredTiger event handler ABI and `WT_UNUSED`. The main utility can pass `verbose_handler` when opening a connection/session to enable human-readable diagnostics.

Risks: Progress output can interleave with other stdout users and is not thread-synchronized. Returning `EIO` from event callbacks may turn output-device failures into command failures. The global pointer exposes a mutable handler object if other code writes through it.

Test signals: Tests can inject the handler and assert routing to stdout/stderr, progress formatting, and error return on closed/broken output streams.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_verbose.c -->
