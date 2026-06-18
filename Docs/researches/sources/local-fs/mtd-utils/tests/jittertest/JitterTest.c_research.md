# File Research: sources/local-fs/mtd-utils/tests/jittertest/JitterTest.c

## Purpose
Measures periodic wakeup jitter while optionally writing to, reading from, and perturbing the filesystem under test.

## Key Elements
Uses a one-shot `ITIMER_REAL` timer and `SIGALRM` handler to measure elapsed time versus expected interrupt period. Writes jitter lines to an output file and console log, pads output to configurable bytes, optionally reads one byte from a test file per tick, optionally captures `/proc/profile` snapshots on high jitter, and optionally sends `SIGSTOP/SIGCONT` to a GC task around writes.

## Dependencies
Uses POSIX timers/signals/scheduler APIs, `mlockall`, `sched_setscheduler`, file I/O, `/proc/profile`, and root privileges for realtime scheduling or GC signaling.

## Behavior/Risks
Signal handler performs non-async-signal-safe work including stdio-like formatting, file I/O, random generation, and profile reads. Several file name buffers are fixed at 33 bytes. The scheduler verification compares `sched_getscheduler()` policy value to requested priority, which is logically wrong.
