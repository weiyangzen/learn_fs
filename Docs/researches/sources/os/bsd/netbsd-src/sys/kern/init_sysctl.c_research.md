# File Research: sources/os/bsd/netbsd-src/sys/kern/init_sysctl.c

## Purpose
Registers and implements many non-base `kern`, `hw`, `debug`, and related sysctl nodes for the full kernel.

## Main Interfaces
- `SYSCTL_SETUP(sysctl_kern_setup)` creates `kern.*` nodes for limits, boot state, vnode/process/file settings, POSIX capability constants, root device/partition, driver listing, coredump settings, build metadata, and message verbosity.
- `SYSCTL_SETUP(sysctl_hw_misc_setup)` creates `hw.usermem`, `hw.usermem64`, and `hw.cnmagic`.
- `SYSCTL_SETUP(sysctl_debug_setup)` conditionally exposes debug variables when `DEBUG` is enabled.
- Handler functions implement validation or computed data for `kern.maxvnodes`, `kern.messages`, `kern.boottime`, `kern.rtc_offset`, `kern.maxproc`, `kern.hostid`, `kern.defcorename`, `kern.cp_time`, `kern.maxptys`, `kern.lwp`, `kern.forkfsleep`, `kern.root_partition`, `kern.drivers`, set-id core settings, CPU IDs, user memory, console magic, root device, and console device.
- `fill_lwp()` copies selected LWP state into `struct kinfo_lwp`.

## Dependencies
Uses sysctl creation/lookup, vnode and VFS drain/reinit paths, kauth authorization, process/LWP locks, CPU iteration, ktrace MIB accounting, device switch conversion tables, console state, UVM accounting, and boot flags.

## Implementation Notes
Several handlers copy kernel snapshots out to user buffers while carefully dropping and reacquiring sysctl locks. `sysctl_kern_lwp()` uses process reference locks and verifies LWP list membership after copyout. Security-sensitive settings use kauth checks before committing changes.

## Research Notes
This file is user-visible kernel ABI surface. Risks are validation mistakes, lock ordering during process/device walks, stale pointer exposure, address exposure policy via `get_expose_address()`, and maintaining compatibility with historic sysctl MIB numbers.
