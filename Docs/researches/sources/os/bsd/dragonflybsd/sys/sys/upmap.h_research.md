# File Research: sources/os/bsd/dragonflybsd/sys/sys/upmap.h

## Summary
Defines mapped per-thread, per-process, and per-CPU kernel/user shared metadata pages.

## Main Responsibilities
- Defines map sizes, versions, element headers, element-length encodings, and element type IDs.
- Defines `/dev/lpmap` thread map fields including signal-blocking coordination and thread title.
- Defines `/dev/upmap` process map fields including runtime ticks, fork ID, pid, vfork indicator, and process title.
- Defines `/dev/kpmap` per-CPU read-only fields including uptime/realtime timespecs, TSC frequency, tick frequency, and fast gettimeofday flag.

## Important Behavior
The header repeatedly warns that absolute field locations can change; userland should scan headers for the desired type and cache only after version validation. `blockallsigs` uses low bits as a nesting count and bit 31 as a pending-signal indicator.

## Risks
This is a shared-memory ABI with explicit atomicity and memory-order expectations. Incorrect userland reads of `sys_kpmap` timestamps can observe torn or stale values unless the documented `upticks` protocol is followed.
