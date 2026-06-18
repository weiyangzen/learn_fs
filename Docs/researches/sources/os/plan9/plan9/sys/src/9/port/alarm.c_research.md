# File Research: sources/os/plan9/plan9/sys/src/9/port/alarm.c

This file implements per-process alarm scheduling and delivery.

Key responsibilities:
- Maintains a sorted linked list of processes with pending alarms.
- `procalarm` sets or clears the current process alarm and returns the previous remaining time in milliseconds.
- `checkalarms` wakes the alarm kernel process when the head alarm expires.
- `alarmkproc` posts `"alarm"` notes to processes whose alarm time has arrived.
- Handles tick wraparound using signed subtraction comparisons.

Filesystem/storage relevance:
- Not filesystem-specific, but timers and sleeping behavior are used throughout kernel services and device operations.
