<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create02.c

Purpose: Ported to new library: 07/2019 Christian Amann <camann@suse.com> Basic error handling test for timer_create(2): Passes invalid parameters when calling the syscall and checks if it fails with EFAULT/EINVAL: 1) Pass an invalid pointer for the sigevent structure parameter 2) Pass an invalid pointer for the timer ID parameter 3) Pass invalid clock type 4) Pass a sigevent with invalid sigev_notify 5) Pass a sigevent with invalid sigev_signo

Important APIs/types/functions: includes `stdlib.h`, `errno.h`, `time.h`, `signal.h`, `tst_test.h`, `lapi/common_timers.h`, `tst_safe_clocks.h`; exercises `syscall`, `time`, `timer_create`, `raw syscall path`; defines `run`, `setup`; uses constants `CLOCK_REALTIME`, `EFAULT`, `EINVAL`, `SIGALRM`, `SIGEV_NONE`, `SIGEV_SIGNAL`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.setup` into the runner. Error-path expectations include `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is POSIX timer objects, clocks, signal/sigevent notification setup, and kernel timer-id allocation.

Dependencies and integration points: Depends on POSIX timers, clock ids, signal/sigevent support, `timer_t` ABI, and realtime clock permissions where applicable. Direct include dependencies include `stdlib.h`, `errno.h`, `time.h`, `signal.h`, `tst_test.h`, `lapi/common_timers.h`.

Risks and test signals: Clock support, signal delivery, and timer limits vary by kernel and libc; stale timers can leak notifications into later cases. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_create/timer_create02.c -->
