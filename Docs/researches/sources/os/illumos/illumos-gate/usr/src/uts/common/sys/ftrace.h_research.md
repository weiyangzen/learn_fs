# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ftrace.h

## Role

`ftrace.h` defines the old fast tracing facility used by kernel and assembly code. It provides tracing state flags, per-event record layout, tunables, and lightweight tracing macros.

## Key Interfaces and Data

- `FTRACE_READY` and `FTRACE_ENABLED` describe global/per-CPU tracing state.
- `ftrace_record_t` stores event string, thread pointer, tick, caller, and up to three data words; LP64 pads the record to a cache-friendly size.
- `FTRACE_NENT` defaults each per-CPU ring buffer to 1024 records.
- Kernel tunables are `ftrace_atboot` and `ftrace_nent`.
- Declares lifecycle and logging functions: `ftrace_init()`, `ftrace_start()`, `ftrace_stop()`, `ftrace_0()` through `ftrace_3_notick()`.
- Defines `ftrace_interrupt_disable()`/`ftrace_interrupt_enable()` and `caller()`.
- Macros `FTRACE_0` through `FTRACE_3` check `CPU->cpu_ftrace.ftd_state` before recording.

## Dependencies and Use

Non-assembly consumers include `sys/thread.h`, `sys/cpuvar.h`, and `sys/types.h`. The constants are intentionally available to assembly via the `_ASM` split.

## Research Notes

The macros are cheap when disabled and rely on per-CPU state rather than a global check. The interface is kernel-only beyond the shared constants.
