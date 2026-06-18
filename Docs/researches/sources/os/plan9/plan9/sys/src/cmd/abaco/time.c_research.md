# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/time.c

Timer facility for Abaco.

Key responsibilities:
- Provides millisecond time from `nsec`.
- Starts a timer server process.
- Maintains a linked list of active timers.
- Lets callers start, stop, or cancel timers.
- Wakes timer channels when their delay expires.
- Uses cancellation flags so stopped timers are not delivered.

Dependencies:
- Uses Plan 9 threads/channels and `sleep`.

Notable risks:
- Timer list is global and simple; correctness depends on the timer process serializing updates through its channel protocol.
