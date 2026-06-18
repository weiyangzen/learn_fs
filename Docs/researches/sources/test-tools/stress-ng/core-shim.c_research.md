# sources/test-tools/stress-ng/core-shim.c

Purpose: implements stress-ng's portability and syscall abstraction layer. It hides libc/kernel feature variation, normalizes some dangerous operations, and provides emulations where stressors need a behavior even when a direct syscall is missing.

Important APIs/types/functions: the file implements the large `shim_*` surface declared in `core-shim.h`. Common families include scheduler/yield, cache flush, file allocation/copy/sync, random/getcpu/gettid, NUMA and memory policy syscalls, mlock/madvise/mincore/statx, futexes, brk/sbrk, string helpers, pkeys, wait/pidfd, new mount API, xattrs, clocks/time, nice/autogroup, deletion wrappers, process/module/sysadmin syscalls, stat wrappers, dirent type emulation, ppoll, namespace/listns, and recent Linux syscalls.

Control flow: most wrappers prefer a libc function when reliable, fall back to `syscall(__NR_*)`, and finally call `shim_enosys`, which sets `errno=ENOSYS` and returns -1. Important exceptions are more behavioral: fallocate can retry without unsupported modes and emulate by writing zero buffers; `shim_posix_fallocate` chunks calls and returns EINTR if stress-ng is stopping; `shim_nanosleep_uint64` retries after EINTR while the continue flag remains set; `shim_waitpid` retries EINTR, sends SIGALRM during shutdown, and eventually force-kills long-stuck children; `shim_kill` refuses dangerous process-group/all-process/root pid cases; unlink/rmdir honor `OPT_FLAGS_KEEP_FILES` and force variants clear chattr flags before retrying; `shim_dirent_type` uses `lstat` if `d_type` is unavailable/unknown.

State and persistence: mostly stateless wrappers. A few functions use static/local persistent state: `shim_posix_fallocate` remembers when to use emulation, `shim_getlogin` returns a static username buffer, and `shim_nice_autogroup` writes `/proc/self/autogroup` while preserving errno. Some wrappers intentionally mutate kernel/process state: scheduling, memory policy, mount, xattr, clocks, modules, pkeys, nice value, filesystem objects, and process signaling.

Dependencies/integration: included broadly by stress-ng core and stressors. It depends on generated feature macros, architecture assembly helpers, CPU feature checks, filesystem helpers, global option flags, signal-name helpers, and continue/shutdown state.

Risks: this file is a compatibility hot spot; missing feature guards can break non-Linux builds. Emulations are semantically approximate and may be slow or alter files (`fallocate` writes zeros). Several wrappers intentionally bypass libc/VDSO to force syscalls for stress coverage. Recent syscalls guarded only by `__NR_*` may compile but fail at runtime with ENOSYS/EPERM.

Test signals: cross-platform compilation, syscall-absent ENOSYS behavior, stop-flag interruption for sleeps/fallocate/waitpid, keep-files behavior, xattr API differences on Apple/Linux, fallocate mode fallbacks, and safety checks around `shim_kill`.
