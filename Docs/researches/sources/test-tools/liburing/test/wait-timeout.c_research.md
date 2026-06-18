# sources/test-tools/liburing/test/wait-timeout.c

Purpose: tests `io_uring_enter` getevents timeout behavior, absolute getevents timers, and registered wait clock support.

Important APIs/types/functions: `timespec_to_ns`, `ns_to_timespec`, `ns_since`, `t_io_uring_wait`, `probe_timers`, `test_timeout`, `test_clock_setup`, `io_uring_enter2`, `io_uring_getevents_arg`, `IORING_ENTER_ABS_TIMER`, `IORING_ENTER_EXT_ARG`, `io_uring_register_clock`, and `IORING_REGISTER_CLOCK`.

Control flow: main probes whether absolute enter timers and registered clocks are supported. If neither exists it skips. Clock setup tests invalid null registration, invalid clock id, valid monotonic and boottime registration, and repeated monotonic registration. It then runs combinations of relative/absolute wait and default/registered clock support. Each `test_timeout` checks current/zero timeout returns promptly with `-ETIME`, expired absolute timeouts return promptly, and a future timeout sleeps roughly one to three seconds.

State/persistence behavior: only ring configuration changes persist during each subtest, especially registered clock id. No external files are created.

Dependencies/integration: uses raw io_uring register/enter syscalls, kernel support for absolute wait timers and `IORING_REGISTER_CLOCK`, monotonic/boottime clocks, and signal mask sizing via `_NSIG`.

Risks/test signals: support is feature-probed by `-EINVAL`. Failures are wrong return code, invalid clock registration accepted, valid clock rejected, or waits firing too early/late.
