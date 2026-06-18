# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/sched.c

## Purpose
Implements POSIX scheduling and NetBSD affinity convenience wrappers.

## Key Elements
Maps process-wide operations to all LWPs with `P_ALL_LWPS`. Provides `sched_setparam`, `sched_getparam`, `sched_setscheduler`, `sched_getscheduler`, priority min/max helpers, `sched_rr_get_interval`, and affinity get/set wrappers.

## Dependencies
Uses `_sched_setparam`, `_sched_getparam`, `_sched_getaffinity`, `_sched_setaffinity`, `sysconf`, `kill`, `errno`, and scheduler constants.

## Behavior/Risks
`SCHED_OTHER` maps to `PRI_NONE`; invalid policies set `EINVAL`. `sched_rr_get_interval` verifies nonzero pid existence with `kill(pid, 0)` and computes nanoseconds from `_SC_SCHED_RT_TS * 1000`.
