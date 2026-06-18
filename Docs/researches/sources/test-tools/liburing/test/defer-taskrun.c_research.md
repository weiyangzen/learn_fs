# sources/test-tools/liburing/test/defer-taskrun.c

Purpose: multi-scenario coverage for `IORING_SETUP_DEFER_TASKRUN`, taskrun flags, eventfd notification, disabled rings, exec cleanup, shutdown processing, and drained writes. Key APIs include `io_uring_get_events`, `io_uring_enable_rings`, `IORING_SETUP_TASKRUN_FLAG`, eventfd helpers, `execve`, socket pairs, and `IOSQE_IO_DRAIN`.

Control flow: after probing support, run disabled-ring/thread tests, child exec with pending direct read, eventfd deferred notification, taskrun flag peek behavior, ring shutdown processing of recv task_work, and drained writev state capture. State is pending task_work, ring flags, eventfd counters, child lifecycle, and optional temp file. Risks include missed task_work, wrong disabled-ring errors, notification timing bugs, and cleanup regressions.
