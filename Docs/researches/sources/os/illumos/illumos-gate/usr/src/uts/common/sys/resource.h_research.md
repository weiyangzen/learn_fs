# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/resource.h

## Role

`resource.h` defines process priority classes, POSIX/BSD resource limits, rlimit/rusage structures, large-file and 32-bit ABI variants, and userland priority/resource APIs.

## Priority and Limits

Priority targets include process, process group, user, group, session, LWP, task, project, zone, and contract.

Resource limits include CPU, file size, data, stack, core, file descriptors, and virtual memory/address space. `RLIM_NLIMITS` is 7.

`rlim_t` and infinity/saved constants vary by LP64 and large-file compilation model. `_SYSCALL32` defines `rlim32_t` and `struct rlimit32`.

## Structures

`struct rlimit` contains current and maximum limits. `struct rlimit64` is available under `_LARGEFILE64_SOURCE`.

`struct rusage` reports user/system time and counters for faults, swaps, block I/O, STREAMS messages, signals, and context switches. `_SYSCALL32` defines `struct rusage32`.

## User APIs

Outside the kernel, the header defines `RUSAGE_SELF`, `RUSAGE_LWP`, and `RUSAGE_CHILDREN`, handles large-file symbol remapping, and declares:
- `setrlimit()`, `getrlimit()`
- optional `setrlimit64()`, `getrlimit64()`
- `getpriority()`, `setpriority()`
- `getrusage()`

## Research Notes

This is a stable ABI header with careful LP64/ILP32 and large-file compatibility. Symbol remapping and saved-limit sentinel values are the most compatibility-sensitive parts.
