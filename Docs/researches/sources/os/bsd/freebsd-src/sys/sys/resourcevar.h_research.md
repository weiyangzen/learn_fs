# File Research: sources/os/bsd/freebsd-src/sys/sys/resourcevar.h

Read completely: 205 lines.

## Purpose
Defines kernel-private resource accounting/statistics structures and APIs for process stats, copy-on-write resource limits, UID resource counters, profiling, rusage aggregation, and limit updates.

## Main Elements
- Defines `struct pstats` with child rusage, interval timers, profiling parameters, and process start time, with zero/copy range markers.
- Defines `struct plimit` as shareable copy-on-write array of `struct rlimit` plus refcount.
- Defines `struct limbatch` helpers for batched limit reference release.
- Defines `struct uidinfo` with per-UID atomic counters for VM/swap reservations, socket buffers, processes, ptys, kqueues, umtxs, pipes, inotify, VMM, refcount, UID, and optional RACCT container.
- Declares profiling update functions, runtime accounting conversion, per-UID counter change functions, `kern_proc_setrlimit`, plimit allocation/copy/fork/free/hold/COW sync, current/max limit accessors, rusage aggregation/fetch, and UID hash/refcount helpers.
- Provides optimized `lim_cur` macro for constant non-VM/data/stack limits.

## Dependencies And Integration
Tied to `resource.h`, `proc.h`, UID credential state, RACCT, process timers/profiling, rusage accounting, and kernel limit enforcement.

## Risk Notes
Plimit COW and UID counters are shared hot paths. Counter increments/decrements must stay balanced, and limit access must account for VM/data/stack dynamic handling rather than only static array reads.
