<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create03.c

Purpose: Regression test for CVE-2017-18344: In kernels prior to 4.14.8 sigevent.sigev_notify is not properly verified when calling timer_create(2) with the field being set to (SIGEV_SIGNAL | SIGEV_THREAD_ID). This can be used to read arbitrary kernel memory. For more info see: https://nvd.nist.gov/vuln/detail/CVE-2017-18344 or commit: cef31d9af908 This test uses an unused number instead of SIGEV_THREAD_ID to check if this field gets verified correctly.

Important APIs/types/functions: includes `errno.h`, `signal.h`, `time.h`, `tst_test.h`, `lapi/common_timers.h`; exercises `time`, `timer_create`, `read`, `raw syscall path`; defines `run`; uses constants `CLOCK_MONOTONIC`, `EINVAL`, `SIGALRM`, `SIGEV_SIGNAL`, `SIGEV_THREAD_ID`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all`, `.tags` into the runner. Named case hints include `CVE`, `linux-git`. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is POSIX timer objects, clocks, signal/sigevent notification setup, and kernel timer-id allocation.

Dependencies and integration points: Depends on POSIX timers, clock ids, signal/sigevent support, `timer_t` ABI, and realtime clock permissions where applicable. Direct include dependencies include `errno.h`, `signal.h`, `time.h`, `tst_test.h`, `lapi/common_timers.h`.

Risks and test signals: Clock support, signal delivery, and timer limits vary by kernel and libc; stale timers can leak notifications into later cases. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create03.c -->
