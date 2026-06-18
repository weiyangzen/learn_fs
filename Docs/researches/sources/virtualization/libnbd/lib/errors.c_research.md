# File Research: sources/virtualization/libnbd/lib/errors.c

Owns thread-local last-error storage for libnbd API calls.

Key structures/functions:
- `struct last_error`: current API context, allocated error string, errno value.
- Constructor creates a pthread TLS key with destructor.
- Destructor frees current thread data but intentionally avoids `pthread_key_delete` due to a documented race.
- `nbd_internal_set_error_context`: records API function context.
- `nbd_internal_set_last_error`: replaces current error string and errno.
- `nbd_internal_get_error_context`: returns current context.
- `nbd_get_error` / `nbd_get_errno`: public accessors for last error.

Interactions:
- `internal.h` defines `set_error` macro around these functions.
- Generated API wrappers set context for functions that may set errors.

Research notes:
- Error state is per-thread, not per-handle.
- If TLS allocation fails, the code falls back to stderr diagnostics rather than losing all error information silently.
