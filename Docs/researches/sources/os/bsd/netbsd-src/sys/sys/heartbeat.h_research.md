# File Research: sources/os/bsd/netbsd-src/sys/sys/heartbeat.h

Read completely: 75 lines.

## Purpose
Declares optional kernel heartbeat instrumentation hooks.

## Main Interfaces
- Kernel-only guard.
- Optional `opt_heartbeat.h`.
- With `HEARTBEAT`: `heartbeat_start`, `heartbeat`, `heartbeat_suspend`, `heartbeat_resume`, `heartbeat_dump`.
- Without `HEARTBEAT`: inline no-op start/heartbeat/suspend/resume.

## Dependencies And Integration
Kernel configuration option controls whether calls compile to real functions or no-ops.

## Risks And Edge Cases
- Header intentionally errors in userland.
- `heartbeat_dump` is declared only when `HEARTBEAT` is enabled.

## Filesystem Relevance
Low. General kernel diagnostic/liveness instrumentation.
