# File Research: sources/os/bsd/netbsd-src/sys/sys/cpu_data.h

Defines the machine-independent per-CPU data embedded in each machine-dependent `cpu_info`.

Key content:
- `enum cpu_count` enumerates per-CPU counters for context switches, syscalls, traps, interrupts, faults, UVM page/fault stats, and sync activity.
- `enum cpu_rel` describes topology peer rings: core, package, first CPU per package.
- `struct cpu_data` stores CPU index, cross-call state, pserialize depth, pending IPIs, scheduler state, topology IDs/siblings, idle LWP, lock counters, softints, UVM/callout/select/vfs-cache per-CPU pointers, lockdebug state, cycle counter metadata, CPU name, per-CPU kcpuset, PCU current LWPs, counters, and heartbeat tracking.
- Many `ci_*` compatibility macros map `struct cpu_info` fields to `ci_data`.
- `CPU_COUNT(idx, d)` updates counters with preemption disabled.
- `cpu_count_get`, `cpu_count`, and `cpu_count_sync`.

Important behavior:
- Comments require adding counters in blocks of 8.
- Structure layout is size-sensitive because many ports embed it in constrained MD CPU structures.
