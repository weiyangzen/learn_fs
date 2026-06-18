# sources/test-tools/fio/os/os-linux-syscall.h

## Purpose
`os-linux-syscall.h` supplies fallback Linux syscall numbers for architectures where libc or kernel headers may not define every number fio needs.

## Important APIs, Types, and Functions
It conditionally defines `__NR_ioprio_set`, `__NR_ioprio_get`, `__NR_fadvise64`, `__NR_sys_splice`, `__NR_sys_tee`, `__NR_sys_vmsplice`, `__NR_shmget`, `__NR_shmat`, `__NR_shmctl`, `__NR_shmdt`, `__NR_preadv2`, and `__NR_pwritev2` for supported architecture macros.

## Control Flow
There is no runtime flow. Preprocessor branches select definitions based on `arch/arch.h` macros such as x86, x86_64, ppc, ia64, alpha, s390, sparc, arm, mips64, sh, hppa, aarch64, loongarch64, and riscv64.

## State and Persistence
No state is stored. The values are used by `syscall()` wrappers in Linux OS and engine code.

## Dependencies and Integration Points
`os-linux.h` includes this header before defining ioprio, gettid, and preadv2/pwritev2 wrappers. Splice engines, fadvise paths, Android/shared-memory paths, and io priority handling may depend on these numbers.

## Risks and Edge Cases
Syscall numbers are architecture ABI constants; wrong values cause hard-to-debug `ENOSYS` or unintended syscall invocation. Some architectures only define subsets, leaving common code to rely on existing system headers or fallback stubs. Unknown architectures emit a warning rather than a hard error.

## Test Signals
Cross-compile builds for each architecture, runtime smoke tests for ioprio and preadv2/pwritev2 where available, and compile checks with old kernel headers are important.
