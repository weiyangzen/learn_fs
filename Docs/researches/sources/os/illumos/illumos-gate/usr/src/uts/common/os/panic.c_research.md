# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/panic.c

## Purpose

`panic.c` implements the architecture-independent panic path. It records panic state, stops other CPUs, prints diagnostic information, optionally enters the debugger, switches storage I/O to polled mode, takes a crash dump, and reboots or halts.

Read completely: 415 lines.

## Panic Model

The opening design comment describes irreversible panic phases: calm, quiesce, sync, and dump. The implementation in this file centers on the quiesce and dump triggers:

- `panic_quiesce`: transition from normal execution into panic quiesce.
- `panic_dump`: transition into dump generation.

The low-level `vpanic()` assembly wrapper records machine registers, switches to `panic_stack` for the first panicking thread, and calls `panicsys()`.

## Key Global State

The first panicking thread records:

- `panic_stack`, reserved for the first panic path.
- `panic_thread`, `panic_cpu`, `panic_regs`, `panic_pcb`, and `panic_reg`.
- `panicstr` and `panicargs`.
- time snapshots: `panic_lbolt`, `panic_lbolt64`, `panic_hrtime`, `panic_hrestime`.
- thread state snapshots: IPL, scheduling flags, bound CPU, preemption count.
- `panic_dip`, used for `dev_err(..., CE_PANIC, ...)`.

Runtime controls include `panic_bootstr`, `panic_bootfcn`, `halt_on_panic`, `nopanicdebug`, `in_sync`, `do_polled_io`, and `panic_forced`.

## `panicsys()` Flow

`panicsys()` raises IPL with `spl8()`, marks the current thread `T_PANIC`, prevents swapping, binds it to the current CPU, increments preemption, and invokes `panic_enter_hw()`.

If the thread is on an interrupt stack and an interrupt thread is available, it preserves the active interrupt stack by swapping in an interrupt-thread stack.

On the first panic-stack entry, it initializes `panicbuf`, records a dump UUID, saves trap or register state, formats the panic message, stops other CPUs with `panic_stopcpus()`, and only then sets `panicstr`. This ordering preserves remote CPU lock-spin state before panic-aware lock bypassing begins.

It then records all one-time panic globals, lowers IPL to clock level, runs hardware quiesce, stops ftrace, executes panic callbacks, flushes kernel log queues, prints the fault-management banner, prints the panic message and optional device prefix, shows trap/register data, and may enter the debugger.

For reentrant panic callers after the first panic, it prints the additional panic message if dump or `panicstr` is already set; otherwise it spins.

## Dump and Reboot

When `panic_trigger(&panic_dump)` succeeds, the code runs `panic_dump_hw()`, lowers IPL to clock level, drains error queues with `errorq_panic()`, sets `do_polled_io = 1`, and calls `dumpsys()`.

If dump was already triggered, it either enters the debugger again or warns that the dump was aborted.

Finally it calls `mdboot()` to halt or reboot according to `halt_on_panic`, `panic_bootfcn`, and `panic_bootstr`. Threads that cannot proceed spin forever with IPL capped at clock level so debugger entry remains possible.

## Platform Dependencies

The file expects machine-dependent support for:

- `panic_savetrap()`
- `panic_saveregs()`
- `panic_stopcpus()`
- `panic_quiesce_hw()`
- `panic_showtrap()`
- `panic_dump_hw()`
- `panic_enter_hw()`

## Notable Invariants

- `panicstr` is intentionally set only after other CPUs are stopped.
- Panic code must be reentrant because debugger sync callbacks and watchdog timeouts can call panic again.
- The first panicking thread owns the reserved panic stack and panic buffer.
- Dump I/O is forced into polled mode before `dumpsys()`.

## Research Relevance

This file is directly relevant to filesystem research because panic handling decides whether the kernel attempts filesystem sync and crash dumps, and because storage drivers must tolerate the polled-I/O panic environment.
