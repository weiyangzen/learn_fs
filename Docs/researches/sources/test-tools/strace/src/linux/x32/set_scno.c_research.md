# sources/test-tools/strace/src/linux/x32/set_scno.c

## Purpose
Uses the x86_64 syscall-number mutation hook for x32, allowing strace to replace the syscall number in a stopped tracee.

## Important APIs, Types, And Functions
The included implementation defines `static int arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)`. It calls `upoke(tcp, 8 * ORIG_RAX, scno)`, writing the original syscall-number slot in the tracee user area. The generic wrapper in `syscall.c` may first use `PTRACE_SET_SYSCALL_INFO`; this hook is the architecture fallback.

## Control Flow
This file delegates fully to `../x86_64/set_scno.c`. Effective flow is a single `upoke` call. In generic control flow, `set_scno` returns `1` if `PTRACE_SET_SYSCALL_INFO` succeeded, `0` if this architecture hook succeeded, and `-1` if the hook failed.

## State And Persistence
No file-local state. On success, the tracee's `ORIG_RAX` register slot is changed, which persists for the current syscall stop and changes the syscall the kernel will execute or report. Generic code owns any associated `struct tcb` bookkeeping.

## Dependencies And Integration Points
Depends on `ORIG_RAX`, `kernel_ulong_t`, `struct tcb`, and `upoke`. On x32, the final ptrace write goes through the raw x86_64 syscall workaround in `ptrace_pokeuser.c`. It integrates with syscall injection, syscall substitution, and any feature that rewrites a tracee's syscall number.

## Risks
The syscall number passed here must already be in the correct personality encoding. For x32 native personality, that often means coordinating with `shuffle_scno_pers` and `__X32_SYSCALL_BIT`; writing an unshuffled number can target the wrong syscall namespace. The `8 * ORIG_RAX` offset assumes the x86_64 user-area layout.

## Test Signals
Tests that replace syscall numbers on x32 should confirm the kernel observes the requested syscall, including x32-native numbers with `__X32_SYSCALL_BIT`. Error-path tests should verify failed ptrace writes propagate as `-1` through generic `set_scno`.

## Source-Read Signal
Reviewed the complete local file and the complete included x86_64 implementation that supplies the effective function.
