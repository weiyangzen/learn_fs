# File Research: sources/os/bsd/freebsd-src/sys/kern/syscalls.c

## Purpose
Generated syscall-name table for the native FreeBSD kernel ABI. It maps syscall numbers to symbolic names used by tracing, diagnostics, auditing, compatibility reporting, and other syscall-number-to-name consumers.

## Main Elements
- `syscallnames[]`: ordered string array from syscall number 0 through 602.
- Includes current native syscall names such as `read`, `write`, `openat`, `kevent`, `copy_file_range`, `timerfd_create`, `kcmp`, `pdrfork`, `pdwait`, and `renameat2`.
- Marks compatibility entries with prefixes such as `compat`, `compat4`, `compat6`, `compat10`, `compat11`, `compat12`, `compat13`, and `compat14`.
- Marks removed or obsolete entries with `obs_...`.
- Marks reserved local-use slots as `"#NNN"`.
- Contains process-descriptor syscalls at 518-520 and 600-601, pipe2 at 542, and timerfd syscalls at 585-587.

## Dependencies And Integration
Automatically generated from the syscall master inputs using configuration from `syscalls.conf`. The table must remain synchronized with syscall numbers, syscall switch generation, headers, libc syscall maps, and compatibility ABIs.

## Risk Notes
This file should not be hand-edited. Any mismatch between this table and the actual syscall switch/header generation would produce misleading tracing or audit names. Reserved and obsolete entries are intentionally retained to preserve syscall-number stability.
