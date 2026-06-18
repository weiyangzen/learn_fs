# File Research: sources/os/bsd/freebsd-src/sys/sys/racct.h

Read completely: 282 lines.

## Purpose
Defines FreeBSD resource accounting identifiers, resource properties, accounting container structure, and RACCT kernel API/stubs.

## Main Elements
- Defines RACCT resource IDs for CPU, data, stack, core, RSS, memlock, process/file/VM counts, IPC resources, wallclock, percent CPU, and I/O rate resources.
- Defines resource property bits for million-scaled values, reclaimable usage, inheritable usage, deniable allocations, sloppy per-credential accounting, and decaying resources.
- Provides macros to query resource properties and whether resource usage can drop.
- Defines `struct racct` with resource counters, linked RCTL rule links, runtime, and timestamp.
- Declares RACCT sysctl node and global enable/type state.
- Under `RACCT`, declares global lock macros and APIs for add/set/subtract, credential accounting, buffer I/O accounting, limits/availability, create/destroy, fork/exit/credential-change handling, moving accounting, and throttling.
- Without `RACCT`, supplies no-op or permissive inline stubs returning success or `UINT64_MAX`.

## Dependencies And Integration
Used by process, credential, jail, UID, and RCTL code to account and enforce resources. Integrates with `struct proc`, `struct ucred`, buffers, sysctl, and global RACCT locking.

## Risk Notes
Resource property classification drives enforcement semantics. Stub behavior means consumers must tolerate RACCT-disabled kernels where accounting calls succeed but do not enforce limits.
