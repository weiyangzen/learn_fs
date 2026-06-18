# File Research: sources/os/bsd/freebsd-src/sys/sys/resource.h

Read completely: 201 lines.

## Purpose
Defines user/kernel resource usage, priorities, resource limits, load average, CPU state, and related syscall prototypes.

## Main Elements
- Defines `id_t` and `rlim_t` typedefs when needed.
- Defines priority range and `PRIO_PROCESS`, `PRIO_PGRP`, `PRIO_USER`.
- Defines `RUSAGE_SELF`, `RUSAGE_CHILDREN`, `RUSAGE_THREAD`, and `struct rusage`.
- Under BSD visibility, defines `struct __wrusage`.
- Defines resource limit IDs from CPU/file/data/stack/core through socket buffers, VMEM/AS, ptys, swap, kqueues, umtx, pipe buffers, and VMM.
- Defines `RLIM_NLIMITS`, `RLIM_INFINITY`, saved limit aliases, optional `rlimit_ident[]`, `struct rlimit`, old 32-bit `struct orlimit`, `struct loadavg`, CPU state indices, and `GETRLIMITUSAGE_EUID`.
- Kernel side declares `averunnable` and `read_cpu_time`; userland side declares `getpriority`, `getrlimit`, `getrusage`, `setpriority`, `setrlimit`, and BSD `getrlimitusage`.

## Dependencies And Integration
Used by process accounting, resource limit enforcement, scheduler/load reporting, libc syscall ABI, RACCT/RCTL mapping, and compatibility limit code.

## Risk Notes
Resource IDs and structure layouts are stable ABI. Adding limits requires synchronized updates across kernel enforcement, userland names, RACCT/RCTL mapping, and compatibility handling.
