# File Research: sources/os/bsd/netbsd-src/sys/sys/resource.h

Read completely: 164 lines.

This public header defines process priority, resource-usage, and resource-limit ABI. It provides `PRIO_*`, `RUSAGE_*`, `struct rusage`, NetBSD `struct wrusage`, `RLIMIT_*` constants, `RLIM_INFINITY`, `struct rlimit`, and NetBSD `struct loadavg`.

Userland prototypes include `getpriority`, `setpriority`, `getrlimit`, `setrlimit`, and versioned `getrusage`. Kernel code also sees `struct orlimit`, `averunnable`, and `dosetrlimit`.

Important details: NetBSD defines 12 resource limits, including socket buffer, address space, and thread-count limits. `RLIM_INFINITY` is the maximum signed 63-bit quantity in an unsigned type.

Risks: layout and constant stability matters for libc, syscalls, core process accounting, and compatibility layers.
