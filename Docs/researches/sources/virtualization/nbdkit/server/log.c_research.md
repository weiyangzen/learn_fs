# File Research: sources/virtualization/nbdkit/server/log.c

Purpose: Central error logging dispatcher and public `nbdkit_error` implementation.

Core behavior:
- `log_verror` preserves incoming `errno`.
- It copies the formatted error message into thread-local storage for structured replies when possible.
- Dispatches to stderr, syslog, configured file, or null logging based on `log_to`.
- Default logging goes to syslog if the server has forked into the background, otherwise stderr.
- Restores `errno` before returning.

Public API:
- `nbdkit_verror(fs, args)` forwards to `log_verror`.
- `nbdkit_error(fs, ...)` is the variadic public entry point for plugins, filters, and server support code.

Important detail:
- Failure to copy the message to thread-local storage is intentionally non-fatal; it is supplementary client-facing information.
