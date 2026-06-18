# File Research: sources/os/plan9/9front/sys/src/cmd/rio/time.c

Timer service for `rio`. A timer process tracks active timers, decrements them using millisecond time from `nsec()`, sends nonblocking expiry notifications, and recycles canceled/expired timers.

Public API: `timerinit()`, `timerstart(dt)`, `timercancel()`, and `timerstop()`. Used by scroll debounce/sleep behavior.
