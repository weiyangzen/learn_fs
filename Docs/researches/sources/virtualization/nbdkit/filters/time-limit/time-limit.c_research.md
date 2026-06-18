# File Research: sources/virtualization/nbdkit/filters/time-limit/time-limit.c

This filter disconnects a client after a configured per-connection elapsed time. It accepts `time-limit`, `time_limit`, or `timelimit`, parsed by `nbdkit_parse_delay`; the default is 60 seconds. Configuration completion converts seconds/nanoseconds to microseconds, with `(0,0)` disabling the filter.

Each handle stores a `struct timeval` captured in `.open`. Before every read, write, trim, zero, extents, or cache request, `check_time_limit` compares current elapsed time with the configured limit. If exceeded, it sets `ESHUTDOWN` when available or `EIO`, calls `nbdkit_disconnect(1)`, and returns failure.

Risks and invariants: the timer starts before the underlying `.open`; a `next` failure currently returns `NULL` without freeing the allocated handle. The disconnect is asynchronous, so the client may not observe the specific errno. Operations not overridden by this filter are not time-gated.
