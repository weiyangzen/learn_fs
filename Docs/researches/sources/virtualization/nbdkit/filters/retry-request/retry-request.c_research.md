# File Research: sources/virtualization/nbdkit/filters/retry-request/retry-request.c

This filter retries failed individual backend calls without reopening the backend connection. Configuration supports `retry-request-retries` (default 2, capped at 1000), `retry-request-delay`, and `retry-request-open=false`.

The `RETRY_START` / `RETRY_END` macros wrap each operation, sleeping before retries and preserving/setting errno on interrupted sleeps. `.open` can retry the initial next-open call; `.get_size`, pread, pwrite, trim, flush, zero, extents, and cache are all retried with the same backend context.

The extents handler recreates a temporary extents object for each retry and copies successful extents back to the caller, avoiding partial extent accumulation across failed attempts.

This filter is appropriate for transient request failures where the connection remains usable. It is not a reconnect/reopen filter; persistent connection failures require the separate `retry` filter.
