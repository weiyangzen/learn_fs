<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq_timed.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq_timed.h

Purpose: extension helper for LTP timed POSIX mqueue tests, adding libc, legacy syscall, and time64 syscall variants plus common timeout/signal test-case metadata.

Important APIs/types/functions: `variants[]` maps each available ABI to `clock_gettime`, `mqt_send`, `mqt_receive`, a `tst_ts` representation, and a human-readable description. `struct test_case` describes descriptor, length, priority, requested timestamp, invalid message/timespec address flags, signal/timeout behavior, expected return, and expected errno. `set_sig()` arms a future absolute timeout and starts a signal-sending helper. `set_timeout()` sets a near-future absolute timeout. `kill_pid()` terminates and waits for the signal helper.

Control flow/state: including tests iterate `variants` through `tst_variant` and use the helper to construct absolute `CLOCK_REALTIME` deadlines. `set_sig()` creates a child process that repeatedly sends `SIGINT`; cleanup must call `kill_pid()` to prevent leaked helpers.

Dependencies/integration: includes `mq.h`, `time64_variants.h`, and `tst_timer.h`, so it bridges POSIX mqueue tests with LTP time64 syscall coverage. Compile-time syscall availability gates the legacy and time64 entries.

Risks/test signals: timing margins are intentionally small for timeout tests and larger for signal interruption; slow systems can turn expected timeout/signal behavior into flakes. Variant-specific failures identify libc wrapper, old kernel timespec, or time64 ABI regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/mq_timed.h -->
