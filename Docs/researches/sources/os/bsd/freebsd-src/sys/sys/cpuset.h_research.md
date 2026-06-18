# File Research: sources/os/bsd/freebsd-src/sys/sys/cpuset.h

## Purpose
Defines CPU affinity bitset operations, cpuset selector constants, kernel cpuset structures, and userland cpuset syscall prototypes.

## Main Elements
- CPU bitset macros wrap generic `__BIT_*` operations for fixed and size-parametrized sets.
- Allocation macros support dynamic CPU set buffers.
- `CPU_LEVEL_*` and `CPU_WHICH_*` constants define affinity query/set targets.
- Reserved cpuset IDs: invalid and default.
- Kernel `struct cpuset` tracks refs, flags, hierarchy links, NUMA domain policy, ID, parent, and CPU mask.
- Kernel APIs manage refs, thread/process affinity, jail roots, interrupt-thread affinity, and string conversions.
- Userland prototypes expose `cpuset()`, set/get ID, and set/get affinity.

## Dependencies And Integration
Includes `_cpuset`, bitset, and queue headers. Implemented by `kern_cpuset.c` and tied to domainset, scheduler affinity, jails, and interrupt routing.

## Risk Notes
Bitset sizes are ABI-relevant. Kernel readers of `cs_mask` may see inconsistent results unless using the documented locking/ref rules.
