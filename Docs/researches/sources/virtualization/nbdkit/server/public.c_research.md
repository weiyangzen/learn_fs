# File Research: sources/virtualization/nbdkit/server/public.c

This file contains miscellaneous public utility APIs exported to nbdkit plugins and filters. Path helpers include `nbdkit_absolute_path` and `nbdkit_realpath`, with Windows behavior using `realpath` replacement semantics. `nbdkit_stdio_safe` reports whether stdin can safely be used during configuration.

`nbdkit_nanosleep` validates duration overflow and, when `ppoll` and `POLLRDHUP` are available, sleeps in a way that wakes early on server shutdown, connection shutdown, socket hangup/error, or invalid socket. The fallback uses ordinary `nanosleep`, with comments warning that shutdown may be delayed on such platforms.

Context-dependent helpers expose the current export name and TLS state. `nbdkit_export_name` reads the thread-local context export name. `nbdkit_is_tls` returns the active connection TLS state, or treats out-of-connection backend opens as TLS only when command-line TLS is required.

The file also manages interned strings through global or per-connection vectors. `nbdkit_strndup_intern`, `nbdkit_strdup_intern`, `nbdkit_vprintf_intern`, and `nbdkit_printf_intern` allocate strings whose ownership is tracked until connection/global cleanup.

`nbdkit_disconnect` lets a plugin or filter request graceful or forced connection shutdown, updating connection status and shutting down writes under the write lock. `nbdkit_name` returns the process name, and `nbdkit_timestamp` returns a UTC timestamp stored in thread-local storage when possible.
