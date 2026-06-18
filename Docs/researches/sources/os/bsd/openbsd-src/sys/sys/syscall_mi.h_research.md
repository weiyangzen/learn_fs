# File Research: sources/os/bsd/openbsd-src/sys/sys/syscall_mi.h

Machine-independent syscall entry/return helpers.

This header implements inline MI syscall processing after MD register setup. `pin_check()` enforces pinsyscalls by verifying the syscall instruction address lies in approved libc/program/ld.so regions or the sigtramp sigreturn slot; failures can KTRACE, print diagnostics, mark accounting, single-thread the process, and abort it.

`mi_syscall()` refreshes credentials, emits tracepoints/DTrace/KTRACE events, validates the userspace stack mapping, runs pin and pledge checks, optionally takes the global kernel lock depending on `SY_NOLOCK`, and invokes the selected `sysent` handler. `mi_syscall_return()` handles tracing and `userret()`, `mi_child_return()` synthesizes fork/vfork/tfork returns for new threads/processes, and `mi_ast()` handles profiling and preemption AST work.

Filesystem/storage relevance: every filesystem syscall crosses this path. Pledge, pinsyscalls, KTRACE, stack validation, and kernel-lock policy all affect VFS syscall execution.
