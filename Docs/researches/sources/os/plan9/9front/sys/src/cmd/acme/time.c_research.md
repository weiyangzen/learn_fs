# File Research: sources/os/plan9/9front/sys/src/cmd/acme/time.c

This file implements Acme's lightweight timer service.

Key responsibilities:
- `msec()` returns current time in milliseconds from `nsec()`.
- `timerstart(dt)` allocates/reuses a `Timer`, resets state, and sends it to the timer process.
- `timerstop(t)` returns a timer to the free list.
- `timercancel(t)` marks a timer canceled.
- `timerinit()` creates the timer channel and starts `timerproc()`.
- `timerproc()` tracks active timers, decrements them based on elapsed milliseconds, wakes expired timers with nonblocking sends, reclaims canceled/expired timers, and receives new timers.

Important dependencies:
- Uses Plan 9 thread channels and `sleep(1)`.
- Used by keyboard tag-commit delay and scroll sleep cancellation behavior.

Filesystem/storage relevance:
- No direct filesystem operations. It supports UI/event timing for Acme's file editor.

Notes:
- Uses nonblocking send on timer expiry to avoid deadlock with clients.
- Timer structs are recycled through a simple free list.
