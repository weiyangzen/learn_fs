# File Research: sources/virtualization/nbdkit/filters/retry/retry.c

This filter retries failed operations by closing and reopening the backend context. Configuration includes `retries` (default 5), `retry-delay`, `retry-exponential`, and `retry-readonly` to force reopened contexts to readonly after failure.

Because `nbdkit_backend_reopen` is not safe against another request on the same connection, `.thread_model` reduces concurrency to `SERIALIZE_REQUESTS`. Each handle stores the original readonly flag, export name, nbdkit context, reopen count, and whether a backend is currently open.

`do_retry` implements retry state: it sleeps, optionally doubles delay, finalizes/closes the old `next`, clears the context's next pointer, opens a fresh backend context with original-or-forced-readonly mode, prepares it, installs it into the context, and tells the caller to retry the data operation. Open itself uses the same logic if the initial next-open fails.

Data callbacks validate request ranges against current size, check backend capabilities before write-like and advisory operations, handle FUA/fast-zero constraints, and retry on failure. Extents are built in a temporary object per attempt and copied back after success. With `retry-readonly`, write/trim/zero requests after a reopen fail with `EROFS`.

The filter can recover from broken backend connections, but it changes connection identity under the client. Operations that are not idempotent, or backends whose state changes between reconnects, require careful deployment.
