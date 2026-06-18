# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/klwp.h

## Purpose
Defines the kernel light-weight process object, per-LWP resource accounting, syscall state, signal/debugger state, timers, contracts, and LWP-global kernel symbols.

## Main Interfaces
- `MAXSYSARGS`: maximum syscall arguments saved per LWP.
- End-of-syscall values:
  - `NORMALRETURN`
  - `JUSTRETURN`
- `struct lrusage`: per-LWP and per-process resource counters.
- `klwp_id_t`: pointer typedef for `_klwp`.
- `klwp_t`: full LWP state structure.
- LWP states:
  - `LWP_USER`
  - `LWP_SYS`
- Kernel symbols under `_KERNEL`:
  - `lwp_default_stksize`
  - `lwp_reapcnt`
  - `lwp_deathrow`
  - `reaplock`
  - `lwp_cache`
  - `segkp_lwp`
  - `lwp0`
  - `lwp_rtt()`

## Dependencies And Relationships
Includes thread, signal, PCB, microstate accounting, ucontext, LWP, and contract headers. It is tightly coupled with `kthread_t`, `proc`, signal delivery, `/proc`, profiling, syscall entry/exit, and contract templates.

## Research Notes
Microstate current state is kept in the thread, while per-LWP accounting arrays live here. The watchpoint array has four slots for exec/write/read/read cases, and syscall arguments are saved inline for restart/inspection paths.
