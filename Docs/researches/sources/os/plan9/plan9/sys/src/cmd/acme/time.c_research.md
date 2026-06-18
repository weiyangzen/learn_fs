# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/time.c

This file implements a lightweight timer service for Acme threads.

Key behavior:
- `timerinit()` creates the timer channel and starts `timerproc()`.
- `timerstart(dt)` allocates/reuses a `Timer`, initializes deadline state, and sends it to the timer proc.
- `timercancel()` marks a timer canceled.
- `timerstop()` returns a timer to the freelist.
- `timerproc()` ticks roughly every millisecond, decrements active timers, nonblocking-sends on expired timer channels, recycles canceled timers, and accepts newly started timers.

Important details:
- Uses millisecond values derived from `nsec()`.
- Handles wrap by dropping a tick.
- Expiry sends are nonblocking to avoid deadlock if a client is simultaneously sending/receiving.

Filesystem relevance:
- Indirect: supports UI delays, tag commit timing, and scroll sleeps.
