# File Research: sources/virtualization/nbdkit/server/threadlocal.c

This file implements nbdkit thread-local storage. Stored data includes an optional thread name, connection instance number, plugin errno value, last server error string, timestamp string, reusable I/O buffer, current connection, and current backend context.

`threadlocal_init` creates the pthread key with a destructor that frees all owned fields. `threadlocal_new_server_thread` allocates and installs an empty record for connection threads. Name and instance-number setters are best-effort metadata for diagnostics.

Thread-local errno and last-error tracking influence client-visible behavior: request handling clears them before backend calls, plugins can set errors, and negotiation error replies can include the last error string when appropriate. `threadlocal_get_errno` preserves process `errno` while reading stored plugin errno.

`threadlocal_buffer` provides one reusable per-thread request buffer, growing it with `realloc` and zeroing the full new allocation when needed. Comments state that old plugin data may remain after use, but the buffer avoids leaking unrelated heap data from the core server.

The file also tracks the active connection and active backend context. Getters validate magic values where safe. Context push/pop supports scoped context switching via the `PUSH_CONTEXT_FOR_SCOPE` macro, with comments explaining why the saved previous context is not revalidated because it may be a freed pointer restored only for stack unwinding.
