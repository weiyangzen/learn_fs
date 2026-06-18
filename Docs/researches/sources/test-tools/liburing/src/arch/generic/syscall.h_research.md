# sources/test-tools/liburing/src/arch/generic/syscall.h

## sources/test-tools/liburing/src/arch/generic/syscall.h

Purpose: Libc-backed syscall wrapper layer for platforms without raw nolibc asm.

Important APIs/functions: `__sys_io_uring_register`, `__sys_io_uring_setup`, `__sys_io_uring_enter2`, `__sys_io_uring_enter`, `__sys_open`, `__sys_read`, `__sys_mmap`, `__sys_munmap`, `__sys_madvise`, `__sys_getrlimit`, `__sys_setrlimit`, `__sys_close`.

Control flow: each wrapper calls libc syscall or direct libc function and normalizes failures to `-errno`; mmap maps `MAP_FAILED` to `ERR_PTR(-errno)`.

State and persistence: invokes kernel syscalls; no internal state.

Dependencies/integration: used by liburing internals where libc is available. Requires syscall numbers for io_uring and standard POSIX headers.

Risks: `__sys_io_uring_enter` hardcodes `_NSIG / 8` signal mask size. Mixed direct libc and `syscall()` wrappers must preserve liburing's negative-error convention.

Test signals: non-nolibc builds across CI; runtime io_uring setup/enter/register behavior.
