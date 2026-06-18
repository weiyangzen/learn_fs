# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_dtrace.c

Read completely: 104 lines.

## Purpose
Provides base kernel hooks and per-process/per-thread storage allocation required for loadable DTrace kernel modules.

## Main Elements
- Declares the `kdtrace_hooks` feature.
- Exposes trap and probe hook globals: `dtrace_trap_func`, `dtrace_doubletrap_func`, `dtrace_pid_probe_ptr`, and `dtrace_return_probe_ptr`.
- Exposes syscall tracing state through `systrace_enabled` and `systrace_probe_func`.
- Defines fixed DTrace storage sizes: `KDTRACE_PROC_SIZE` and `KDTRACE_THREAD_SIZE`.
- Implements process/thread constructors and destructors that allocate and free `p_dtrace` and `td_dtrace` from `M_KDTRACE`.

## Dependencies And Integration
Used by machine-dependent trap handlers, syscall tracing, process/thread lifecycle code, and DTrace modules loaded after boot.

## Risk Notes
The fixed storage sizes form an ABI-like contract with DTrace consumers. Hook globals are intentionally nullable and must be checked/managed by provider modules.
