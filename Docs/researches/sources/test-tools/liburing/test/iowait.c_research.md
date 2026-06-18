<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/iowait.c -->
## sources/test-tools/liburing/test/iowait.c

Purpose: tests `io_uring_set_iowait` toggling on kernels advertising `IORING_FEAT_NO_IOWAIT`.

Important APIs/types/functions: `get_iowait`, `test`, `io_uring_set_iowait`, `/proc/stat`, `sched_setaffinity`, `io_uring_wait_cqe_timeout`, and `IORING_FEAT_NO_IOWAIT`.

Control flow: `main` pins the process to CPU 0, creates a ring, and runs `test` first with iowait disabled then enabled. Each scenario submits a pipe read that will block, records CPU0 iowait from `/proc/stat`, waits one second with timeout, closes pipe fds to complete the read, reaps the CQE, and checks iowait delta is small when disabled and large when enabled.

State and persistence behavior: ring iowait mode is mutable per scenario. `/proc/stat` provides external CPU accounting state.

Dependencies and integration points: depends on scheduler affinity, procfs accounting, pipe blocking reads, and kernel iowait feature support.

Risks: CPU accounting thresholds can be noisy in virtualized or busy systems. Lack of affinity permission causes skip.

Test signals: pass means io_uring wait accounting can be toggled and affects CPU iowait reporting as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/iowait.c -->
