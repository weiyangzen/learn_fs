# File Research: sources/virtualization/nbdkit/server/timeout.c

This file implements optional per-connection timeouts when `HAVE_TIMEOUT_OPTION` is available. `start_timeout` creates a one-shot `CLOCK_MONOTONIC` POSIX timer using `SIGEV_THREAD`, with the connection pointer passed to the callback, then arms it from global `timeout_secs` and `timeout_nsecs`.

The timeout callback takes the connection lock, verifies the connection magic, timer state, active status, and valid socket, then calls `shutdown(conn->sockout, SHUT_RDWR)` and marks the connection dead. Comments emphasize that this runs asynchronously from another thread and intentionally does minimal work; `shutdown` is preferred over `close` to avoid fd reuse hazards.

`cancel_timeout` deletes an active timer and clears the `timer_set` flag. When timeout support is not compiled in, both start and cancel functions are no-ops.
