<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create01.c

Purpose: Ported to new library: 07/2019 Christian Amann <camann@suse.com> Basic test for timer_create(2): Creates a timer for each available clock using the following notification types: 1) SIGEV_NONE 2) SIGEV_SIGNAL 3) SIGEV_THREAD 4) SIGEV_THREAD_ID 5) NULL This is also regression test for commit: f18ddc13af98 ("alarmtimer: Use EOPNOTSUPP instead of ENOTSUPP")

Important APIs/types/functions: includes `signal.h`, `time.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/common_timers.h`; exercises `time`, `timer_create`, `raw syscall path`; defines `run`; uses constants `CLOCK_MONOTONIC_RAW`, `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`, `SIGALRM`, `SIGEV_NONE`, `SIGEV_SIGNAL`, `SIGEV_THREAD`, `SIGEV_THREAD_ID`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.needs_root`, `.tags` into the runner. Named case hints include `linux-git`. Error-path expectations include `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is POSIX timer objects, clocks, signal/sigevent notification setup, and kernel timer-id allocation.

Dependencies and integration points: Depends on POSIX timers, clock ids, signal/sigevent support, `timer_t` ABI, and realtime clock permissions where applicable. Direct include dependencies include `signal.h`, `time.h`, `tst_test.h`, `tst_safe_macros.h`, `lapi/common_timers.h`.

Risks and test signals: Clock support, signal delivery, and timer limits vary by kernel and libc; stale timers can leak notifications into later cases. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create01.c -->
