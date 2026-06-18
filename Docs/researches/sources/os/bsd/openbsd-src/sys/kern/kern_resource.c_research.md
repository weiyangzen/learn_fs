# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_resource.c

Purpose: Implements priority syscalls, resource limits, CPU/runtime accounting, rusage aggregation, RLIMIT_CPU enforcement, and copy-on-write `plimit` structures.

Key behavior:
- `sys_getpriority()` and `sys_setpriority()` operate over process, process group, or user selection.
- `donice()` enforces ownership/root rules and updates all threads' scheduler priorities.
- `sys_setrlimit()` copies user limits and delegates to `dosetrlimit()`.
- `dosetrlimit()` serializes updates with `rlimit_lock`, clamps global maxima, adjusts stack VM protections for `RLIMIT_STACK`, and arms CPU-limit checking.
- `sys_getrlimit()` reads from the thread's cached `plimit`.

Accounting:
- `tuagg_sumup()`, `tuagg_get_proc()`, `tuagg_get_process()`, `tuagg_add_process()`, and `tuagg_add_runtime()` aggregate thread/process runtime and tick accounting using producer/consumer generation fields.
- `calctsru()` and `calcru()` convert statclock ticks into user/system/interrupt time.
- `dogetrusage()` builds `RUSAGE_SELF`, `RUSAGE_THREAD`, and `RUSAGE_CHILDREN`.
- `rucheck()` sends `SIGXCPU` at intervals and `SIGKILL` after hard CPU-limit breach.

Filesystem relevance:
- `RLIMIT_NOFILE` is clamped by `maxfiles`.
- `RLIMIT_CORE` is consumed by `kern_sig.c` coredump logic.
- Stack limit changes directly alter VM map protections through UVM.

Limit sharing model:
- `lim_startup()` initializes default limits and the `plimit` pool.
- `lim_fork()` shares limits after fork.
- `lim_write_begin()` and `lim_write_commit()` implement copy-on-write replacement.
- `lim_read_enter()` caches process limits per thread.
