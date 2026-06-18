<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_event.c -->
# sources/user-network-fs/samba/source3/lib/util_event.c

## Purpose
`util_event.c` implements a repeating idle timer helper around `tevent`.

## Important APIs, types, and functions
`struct idle_event` stores the current timer, interval, debug name, callback, and private data. Public API `event_add_idle` allocates and schedules the event. `smbd_idle_event_handler` invokes and reschedules it.

## Control flow
`event_add_idle` schedules the first timer for current time plus interval. When fired, the handler frees the old timer, calls the user callback, frees the entire idle event if the callback returns false, or schedules a new timer at `now + interval` if true.

## State and persistence behavior
The idle event is talloc-owned under the caller's memory context and persists only while callbacks continue returning true. No persistent state is written.

## Dependencies and integration points
It depends on `tevent`, timeval helpers, talloc, SMB assertions, and debug logging. smbd-style event loops use it for periodic housekeeping.

## Risks and edge cases
Reschedule allocation failure triggers an assertion. Callback code controls lifetime by boolean return and must be safe to run from the event loop.

## Test signals
Tests should verify initial scheduling, repeated callbacks, stopping on false, and cleanup behavior when the event talloc context is freed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_event.c -->
