# sources/test-tools/strace/src/linux/x32/set_error.c

## Purpose
Uses the x86_64 register-mutation implementation for injecting syscall error and success results on x32.

## Important APIs, Types, And Functions
The included implementation defines `static int arch_set_error(struct tcb *tcp)` and `static int arch_set_success(struct tcb *tcp)`. `arch_set_error` computes `-(long) tcp->u_error`; `arch_set_success` uses `tcp->u_rval`. Both update the cached register view, choosing `i386_regs.eax` when `tcp->currpers == 1` and `x86_64_regs.rax` otherwise, then call `upoke(tcp, 8 * RAX, rval)` to write the tracee register.

## Control Flow
This file has only an include directive, so effective control flow is inherited from x86_64. The generic `set_error`/success logic in `syscall.c` first tries `PTRACE_SET_SYSCALL_INFO` when available, then falls back to these architecture hooks. The architecture hook writes the result register and returns `upoke` status; generic code restores cached `tcp` fields or refreshes error state depending on success.

## State And Persistence
Mutates `tcp->u_error`/`tcp->u_rval` indirectly through the generic caller and mutates architecture register caches directly. On successful `upoke`, the tracee's `RAX` slot is persistently changed for the stopped tracee, affecting the syscall result observed when it resumes. There is no file-local static state.

## Dependencies And Integration Points
Depends on `struct tcb`, `kernel_ulong_t`, `i386_regs`, `x86_64_regs`, `RAX`, and `upoke`. For x32, `upoke` uses the x32 `ptrace_pokeuser.c` workaround, so this include chain connects syscall fault injection to raw x86_64 ptrace writes. It integrates with `syscall.c`'s injection paths for `--inject`, syscall tampering, and result forcing.

## Risks
Personality selection is critical: `currpers == 1` writes the i386 cached register while other personalities write the x86_64/x32 cache. A mismatch between cached register state and ptrace offsets can produce stale displays or failed injection. Error values greater than `MAX_ERRNO_VALUE` are filtered by generic code, but architecture code still assumes the converted negative result fits the tracee ABI.

## Test Signals
Syscall injection tests on x32 should verify both forced errno and forced success return values. Multi-personality tests should cover `currpers == 1` and native x32 behavior. Failures in `upoke` should produce generic rollback behavior and an error message unless the tracee exited.

## Source-Read Signal
Reviewed the complete local file and the complete included x86_64 implementation that supplies the effective functions.
