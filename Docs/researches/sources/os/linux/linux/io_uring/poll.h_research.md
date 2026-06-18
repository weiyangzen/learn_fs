# File Research: sources/os/linux/linux/io_uring/poll.h

Header for io_uring poll state and poll operation entry points.

Key responsibilities:
- Defines `struct io_poll` waitqueue state and `struct async_poll` wrapper for poll-driven retry.
- Defines async-poll result codes: ok, aborted, ready.
- Exposes poll add/remove prep and issue functions.
- Exposes async poll arming, cancellation, teardown, and task_work callback entry points.
- Provides `io_poll_multishot_retry()` for callers that already own a multishot poll request.

Important invariants:
- `io_poll_multishot_retry()` is only valid when the caller is in multishot issue context or otherwise owns the request.
- `double_poll` is allocated only when a file registers a second distinct waitqueue.
