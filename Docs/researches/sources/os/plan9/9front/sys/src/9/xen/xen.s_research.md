# File Research: sources/os/plan9/9front/sys/src/9/xen/xen.s

Purpose: Plan 9 x86 assembly glue for Xen callbacks and hypercall entry.

Key interfaces:
- `hypervisor_callback`: saves a Plan 9 `Ureg`-compatible frame, fixes segment registers, calls `xenupcall`, restores state, and returns with `IRETL`.
- `failsafe_callback`: nominal Xen failsafe callback path; currently begins with immediate `IRETL`, leaving later repair code unreachable.
- `xencall1` through `xencall6`: fall-through wrappers that load hypercall op/args into x86 registers and execute `INT $0x82`.

Integration notes: Used by `xensystem.c` hypercall wrappers. Includes `xendefs.h` and `mem.h`.

Risk/attention points: The source comments call out a race where an upcall can stack between `spllo()` and `rti`. The failsafe callback has unreachable handler-install code after `IRETL`.
