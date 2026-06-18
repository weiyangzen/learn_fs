# File Research: sources/os/bsd/dragonflybsd/sys/sys/user.h

## Summary
Userland compatibility header for programs that need kernel process information structures.

## Main Responsibilities
- Rejects inclusion from kernel builds.
- Forces `_KERNEL_STRUCTURES` so userland sees kernel-structure layouts.
- Includes types, errno, time, resource, credential, iovec/uio, process, lock, VM, pmap, resourcevar, signalvar, PCB, and kinfo definitions.

## Important Behavior
The header explicitly calls itself a hack for user programs that need `kinfo_proc` and related kernel structures.

## Risks
Including this header exposes userland to kernel layout churn and broad transitive dependencies. It should be treated as a compatibility/debugging interface, not a stable high-level API.
