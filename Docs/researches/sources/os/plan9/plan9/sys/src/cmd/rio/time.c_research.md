# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/time.c

Read status: complete, 124 lines.

This file provides a small timer service for `rio`. `timerinit` creates a channel and starts `timerproc`; `timerstart` allocates or reuses a `Timer`, sets duration, and sends it to the timer process. `timercancel` marks a timer canceled; `timerstop` returns it to a free list.

`timerproc` tracks active timers, decrements them based on millisecond time from `nsec`, sends nonblocking expiration notifications, handles cancellation, and receives newly scheduled timers.

Filesystem relevance: no direct filesystem logic; supports UI timing such as scrollbar repeats.
