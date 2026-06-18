# File Research: sources/os/bsd/freebsd-src/sys/sys/ptrace.h

Read completely: 281 lines.

## Purpose
Defines the `ptrace(2)` request ABI, event masks, data structures, and kernel helper prototypes for process/thread debugging, memory/register access, syscall tracing, VM map inspection, coredump requests, and remote syscalls.

## Main Elements
- Defines standard ptrace requests from `PT_TRACE_ME` through `PT_SC_REMOTE`, plus machine-specific ranges and kernel-internal request range.
- Includes machine-specific ptrace extensions from `<machine/ptrace.h>`.
- Defines ptrace event mask bits for exec, syscall entry/exit, fork, LWP, and vfork.
- Defines `struct ptrace_io_desc` and PIOD read/write operation constants.
- Defines `struct ptrace_lwpinfo` and 32-bit variant with event, flags, signal state, thread name, child pid, and syscall metadata.
- Defines syscall return, VM map entry, coredump, and remote syscall argument structures.
- Under `_KERNEL`, defines coredump/syscall request carrier structs and declares register, single-step, machine-dependent, memory I/O, compat32 register, and unsuspend helpers.
- Declares userland `ptrace()` and exposes `allow_ptrace` in-kernel.

## Dependencies And Integration
Integrated with signals, machine registers, proc/thread state, procfs/linprocfs, VM maps, vnode coredump output, syscall argument handling, compat32, and process debug flags from `proc.h`.

## Risk Notes
This is a debugger ABI. Request numbers, structure layouts, flag meanings, and compat32 translations must remain stable. Kernel helpers must preserve stopped-process, thread-suspension, and register-access invariants.
