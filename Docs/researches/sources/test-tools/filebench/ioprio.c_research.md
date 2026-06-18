<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/ioprio.c -->
# sources/test-tools/filebench/ioprio.c

Purpose: optionally sets Linux per-thread/process I/O priority for Filebench worker threads when built with `HAVE_IOPRIO`.

Important APIs/functions: local inline wrappers call `syscall(__NR_ioprio_set)` and `syscall(__NR_ioprio_get)`. `set_thread_ioprio(threadflow_t *tf)` reads `tf->tf_ioprio`, rejects values above 7, sets best-effort class priority, reads back the low priority bits, and logs the result.

Control flow: `flowop_start()` calls `set_thread_ioprio()` before runtime flowop creation. If the syscall fails, the function logs an error and continues without aborting the workload.

State/persistence: changes kernel I/O priority for the current process/thread context. No Filebench shared state is changed beyond logs.

Dependencies/integration: depends on `filebench.h`, `ioprio.h`, AVD evaluation, Linux syscall numbers, and Filebench logging. Header compiles to a no-op when unsupported.

Risks: the implementation hardcodes best-effort class and silently ignores priorities greater than 7. Permission or kernel support failures only log. The syscall target `IOPRIO_WHO_PROCESS, who=0` relies on Linux semantics for current task/process.

Test signals: Linux builds with and without `HAVE_IOPRIO`; WML thread `ioprio` values 0, 7, 8; tests should verify no-op behavior on unsupported platforms and nonfatal logging on permission failure.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/ioprio.c -->
