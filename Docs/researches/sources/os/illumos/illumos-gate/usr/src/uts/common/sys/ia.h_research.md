# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ia.h

## Role

`ia.h` defines kernel-private state for the interactive scheduling class, historically related to time-sharing scheduling with interactive boosts.

## Key Interfaces and Data

- Debug/priority macros include `dcmn_err`, `IA_OFF_QUANTUM`, `IA_OFF_PRIORITY`, `iaumdpri`, and `iamedumdpri`.
- `iadpent_t` is an interactive dispatch parameter table entry: global priority, quantum, priority after time-quantum expiration, priority after sleep return, max wait, and long-wait priority.
- `iaproc_t` is per-thread interactive scheduling state: remaining quantum, CPU-controlled priority component, user priority limit, user priority, user-mode priority, nice value, flags, dispatch wait, thread pointer, process/thread flag pointers, list links, and interactive mode.
- Flags include `IABACKQ` for back-of-queue after preemption and `IASLEPT` for long-term suspend/new slice handling.

## Dependencies and Use

The header includes `sys/types.h` and `sys/thread.h`. Userland priocntl structures are in `iapriocntl.h`.

## Research Notes

The per-thread structure stores pointers into process/thread state (`p_stat`, `t_pri`, `p_flag`) so scheduler code can update related state efficiently.
