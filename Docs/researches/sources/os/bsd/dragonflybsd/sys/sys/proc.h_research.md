# File Research: sources/os/bsd/dragonflybsd/sys/sys/proc.h

Kernel process, LWP, process group, session, and process-management interface definitions.

Key responsibilities:
- Rejects direct userland inclusion; userland must include `sys/user.h`.
- Includes process dependencies for callouts, CPU masks, file descriptors, queues, trees, priorities, signals, locks, credentials, events, sysent, threads, scheduler, resources, machine proc state, and signal vars.
- Defines list and RB tree heads for processes, process groups, sessions, and LWPs.
- Defines `struct session`, `struct pgrp`, `struct pargs`, `struct lwp`, `struct proc`, and `struct procglob`.
- Defines process, LWP, and LWP MP-state flags.
- Defines macros for LWP iteration, single-LWP assertion, session leader, jail credential check, stop events, process/LWP holds, and process stall.
- Declares global process/thread roots and many kernel process lifecycle, lookup, group/session, scheduling, fork/exit, hold/release, user mapping, and reaper APIs.

Important behavior:
- `struct proc` contains shared process-wide state; `struct lwp` contains schedulable lightweight-process/thread-specific state.
- `p_startcopy`/`p_endcopy` and `lwp_startcopy`/`lwp_endcopy` mark fork-copy regions.
- Process lists are protected by `proc_token` inside `struct procglob`.
- `ONLY_LWP_IN_PROC()` panics if used on a multi-threaded process.
- `PHOLD/PRELE` and `LWPHOLD/LWPRELE` prevent destruction while other subsystems operate on objects.
- Reaper support is integrated through `p_reaper`, `p_deathsig`, and reaper APIs.

Dependencies:
- Kernel-only and kernel-structures consumers.
- Tightly coupled to scheduler, signal, VM, VFS/namecache, procfs, ptrace, jail, kqueue, sysent, and machine-dependent process code.

Notable risks:
- This is high-blast-radius kernel ABI/internal structure layout.
- Several fields are compatibility placeholders or deprecated markers; removing or reusing them affects kernel modules/crash tools.
- Process and LWP hold/lock/reference protocols are critical for ptrace, procfs, signals, and exit races.
