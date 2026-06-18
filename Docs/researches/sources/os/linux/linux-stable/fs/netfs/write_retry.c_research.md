# File Research: sources/os/linux/linux-stable/fs/netfs/write_retry.c

Retries short or retryable write subrequests.

Key behavior:
- Waits for all active streams to quiesce before retry list surgery.
- Calls filesystem `retry_request()` for upload streams when available.
- Reissues directly when no prepare hook is needed.
- Otherwise rebuilds contiguous retry spans, calls stream `prepare_write()` to renegotiate limits, repartitions iterators, and reissues.
- Allocates extra subrequests if a span expands into more pieces; discards excess subrequests if fewer pieces are needed.
- Handles upload and cache streams independently.
- Contains TODO placeholders for future content-encryption read-modify-write retry handling.
