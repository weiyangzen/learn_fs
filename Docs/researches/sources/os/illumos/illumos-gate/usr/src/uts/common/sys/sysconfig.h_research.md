# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysconfig.h

## Purpose
Defines command numbers for the undocumented `_sysconfig` system call and declares the machine-specific kernel helper.

## Main Interfaces
- Kernel-only `mach_sysconfig(int)`.
- `_CONFIG_*` command constants for configured limits and machine characteristics:
  - process, group, open-file, page-size, clock tick, POSIX/X/Open version values
  - processor counts, async I/O, message queues, realtime signals, semaphores, timers
  - physical/available pages and cache/coherency data
  - max PID, stack protection, CPU ID, symlink loop max, ephemeral ID max, user address max, and `NCPU`.

## Dependencies And Relationships
Used by the `_sysconfig` syscall implementation and architecture-specific code that supplies machine-dependent values.

## Research Notes
The file explicitly warns that `_sysconfig` is undocumented and not a stable future-compatibility interface. Command values are numeric ABI and must be treated as fixed.
