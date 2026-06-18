# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/clock_getcpuclockid.c

## Purpose
Provides the POSIX-style `clock_getcpuclockid` API.

## Key Elements
Calls `clock_getcpuclockid2(P_PID, (id_t)pid, clock_id)` and returns an error number instead of setting `errno` as the function result.

## Dependencies
Uses `<time.h>`, `<errno.h>`, `pid_t`, `id_t`, and `P_PID`.

## Behavior/Risks
It saves and restores `errno`, so callers receive errors through the return value. This wrapper must preserve POSIX's non-`-1` error convention.
