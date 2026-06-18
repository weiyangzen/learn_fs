# sources/test-tools/liburing/src/arch/syscall-defs.h

## sources/test-tools/liburing/src/arch/syscall-defs.h

Purpose: Architecture-independent typed wrappers built on raw `__do_syscallN` macros.

Important APIs/functions: `__sys_open`, `__sys_read`, `__sys_mmap`, `__sys_munmap`, `__sys_madvise`, `__sys_getrlimit`, `__sys_setrlimit`, `__sys_close`, `__sys_io_uring_register`, `__sys_io_uring_setup`, `__sys_io_uring_enter2`, `__sys_io_uring_enter`.

Control flow: `__sys_open` uses `open` or `openat` depending on syscall availability; `__sys_mmap` uses `mmap2` with page-shifted offset when present; rlimit wrappers use `prlimit64`; io_uring wrappers call the corresponding syscalls; `__sys_io_uring_enter` supplies `_NSIG/8` mask size.

State and persistence: performs direct kernel syscalls, returning raw integer/pointer results.

Dependencies/integration: included by architecture raw syscall headers; consumed by nolibc liburing code and page-size helpers.

Risks: unlike generic libc wrappers, raw syscall return values are not converted through `errno`; callers must expect negative kernel errno. Mmap returns a cast pointer without `ERR_PTR` normalization. `_NSIG` assumptions must match kernel ABI.

Test signals: nolibc builds and io_uring setup/register/enter functionality on supported architectures.
