# File Research: sources/os/bsd/freebsd-src/sys/sys/sysent.h

## Scope

This header defines FreeBSD kernel syscall dispatch metadata, per-ABI execution vectors, syscall module registration helpers, and shared-page/sysvec initialization declarations. It is a central contract between generated syscall tables, kernel syscall handlers, executable image activation, ABI compatibility layers, auditing, and DTrace systrace.

## APIs And Constants

- Defines `sy_call_t` syscall handler signature and systrace probe/argument callback types.
- Defines `struct sysent`, the syscall table entry: handler, optional systrace arg translator, argument count, syscall flags, audit event, DTrace probe IDs, and thread-count state.
- Defines syscall flags such as `SYF_CAPENABLED` and thread state flags `SY_THR_STATIC`, `SY_THR_DRAINING`, `SY_THR_ABSENT`, and `SY_THR_INCR`.
- Defines `struct sysentvec`, the executable ABI vector containing syscall table pointers, signal delivery, core dump, auxv/string copyout, register setup, limits, syscall argument fetching, shared-page/vDSO offsets, thread hooks, trap hook, hardware capability pointers, exec/exit protection hooks, set-id policy, fork return handling, and regset ranges.
- Defines sysvec flags for ABI width and behavior: `SV_ILP32`, `SV_LP64`, `SV_AOUT`, `SV_SHP`, `SV_SIGSYS`, `SV_TIMEKEEP`, `SV_ASLR`, `SV_RNG_SEED_VER`, `SV_SIG_DISCIGN`, `SV_SIG_WAITNDQ`, and `SV_DSO_SIG`.
- Defines ABI constants `SV_ABI_LINUX`, `SV_ABI_FREEBSD`, and `SV_ABI_UNDEF`, plus process/current-process access macros.
- Under `_KERNEL`, declares the native `sysent[]`, `syscallnames[]`, `nosys_sysent`, `nosys()`, loadable syscall placeholders, registration/deregistration helpers, shared-page helpers, and exec sysvec initialization hooks.
- Provides `SYSENT_INIT_VALS`, `MAKE_SYSENT`, `SYSCALL_MODULE`, `SYSCALL_MODULE_HELPER`, `SYSCALL_INIT_HELPER*`, and related helper macros for static and loadable syscall definitions.

## Control Flow And Integration

- Kernel syscall dispatch indexes a `struct sysentvec` selected by the process ABI, then a `struct sysent` selected by syscall number.
- Syscall modules register by replacing a slot in a syscall table while preserving the old `struct sysent` for deregistration.
- Syscall helper arrays support bulk registration with per-helper `registered` state so partial setup can be unwound.
- Systrace hooks are conditionally active when `KDTRACE_HOOKS` is present; otherwise `SYSTRACE_ENABLED()` folds to zero.
- `sysentvec` integrates executable loading with machine-dependent register setup, signal trampoline placement, shared page/vDSO mapping, ABI-specific syscall argument fetch/return semantics, and process/thread lifecycle hooks.

## Dependencies

- Includes BSM audit definitions and uses `au_event_t` for per-syscall audit classification.
- Refers to core kernel types such as `thread`, `proc`, `image_params`, `trapframe`, `vnode`, `rlimit`, `ksiginfo`, `coredump_writer`, and `note_info_list`.
- Ties into module loading, SYSINIT ordering, exec image activation, signal delivery, ptrace/core dump paths, and DTrace systrace.

## Risks And Invariants

- `struct sysent` field layout and `SYSENT_INIT_VALS` must remain consistent with generated syscall code and syscall table initializers.
- `struct sysentvec` is ABI-critical; changing hooks, flags, or address fields affects every process using that ABI.
- Loadable syscall registration must preserve and restore old entries exactly to avoid stale handlers or wrong audit metadata.
- `SYF_CAPENABLED` is part of Capsicum syscall policy; incorrect flags can expose or block syscalls in capability mode.
- Thread-count state flags protect dynamic syscall unload from racing active syscall execution.
