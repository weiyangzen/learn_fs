# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ftrace.c

## Purpose

`ftrace.c` implements a low-overhead per-CPU fast tracing facility with circular buffers, global enable/disable state, dynamic CPU configuration support, and trace-record writers for zero to three arguments.

Read completely: 528 lines.

## Main Responsibilities

- Initializes global tracing state with `ftrace_init()`.
- Lazily initializes per-CPU tracing state in `ftrace_cpu_init()`.
- Allocates per-CPU ring buffers on first start through `ftrace_cpu_start()`.
- Stops tracing globally and per CPU.
- Frees per-CPU buffers during CPU unconfiguration in `ftrace_cpu_fini()`.
- Registers CPU dynamic reconfiguration callbacks.
- Records trace events through `ftrace_0()`, `ftrace_1()`, `ftrace_2()`, `ftrace_3()`, and `ftrace_3_notick()`.

## State Model

Global state uses `ftrace_state` with `FTRACE_READY` and `FTRACE_ENABLED`.

Each CPU has `cpu_ftrace.ftd_state`, `ftd_first`, `ftd_last`, and `ftd_cur`. `FTRACE_READY` means the CPU can trace. `FTRACE_ENABLED` means trace calls on that CPU may append records.

`ftrace_atboot` starts tracing during init if set. `ftrace_nent` controls per-CPU ring size.

## Locking And Trace Context

`ftrace_lock` protects global and per-CPU state transitions and buffer pointer assignment. Trace-context writers do not take this lock. Instead, they disable interrupts, recheck the per-CPU enabled bit, write one fixed-size record, advance the circular pointer, and restore interrupts.

This design avoids blocking in tracing paths and relies on CPU power-off state to make buffer freeing safe.

## CPU Dynamic Reconfiguration

`ftrace_cpu_setup()` responds to `CPU_CONFIG` by initializing the CPU and starting it if global tracing is enabled. It responds to `CPU_UNCONFIG` by finalizing the CPU trace state, requiring the CPU to be powered off before freeing its buffer.

## Trace Records

The trace functions store:

- event string pointer
- current thread
- timestamp from `gethrtime_unscaled()` except `ftrace_3_notick()`
- caller
- up to three data arguments

Buffers wrap from `ftd_last` back to `ftd_first`.

## Important Invariants

- `ftrace_nent < 1` prevents initialization.
- Per-CPU buffers are allocated lazily and published with `membar_producer()`.
- Buffer freeing only occurs when the CPU is powered off.
- Trace calls must tolerate stale global state reads and rely on the per-CPU enabled check.

## Research Relevance

This file is not filesystem-specific, but it provides a kernel tracing substrate that can capture low-level storage, VFS, and scheduler events with low overhead when instrumented callers use ftrace macros.
