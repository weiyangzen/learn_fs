<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime03.c

Purpose: CVE 2018-12896 Check for possible overflow of posix timer overrun counter. Create a CLOCK_REALTIME timer, set extremely low timer interval and expiration value just right to cause overrun overflow into negative values, start the timer with TIMER_ABSTIME flag to cause overruns immediately. Then just check the overrun counter in the timer signal handler. On a patched system, the value returned by timer_getoverrun() should be capped at INT_MAX and not allowed to overflow into negative range. Bug fixed in: commit 78c9c4dfbf8c04883941445a195276bb4bb92c76 Date: Tue Jun 26 15:21:32 2018 +0200 posix-timers: Sanitize overrun handling Signal handler will be called twice in total because kernel will schedule another pending signal before the timer gets disabled.

Important APIs/types/functions: includes `unistd.h`, `signal.h`, `time.h`, `limits.h`, `tst_test.h`, `tst_safe_clocks.h`; exercises `time`, `timer_getoverrun`; defines `sighandler`, `setup`, `run`, `cleanup`; uses constants `CLOCK_REALTIME`, `SIGEV_SIGNAL`, `SIGUSR1`.

Control flow centers on `sighandler`, `setup`, `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.tags` into the runner. Named case hints include `linux-git`, `CVE`.

State and persistence behavior: Runtime state is POSIX timer arming/disarming, absolute versus relative mode, invalid timespec validation, and signal delivery.

Dependencies and integration points: Depends on POSIX timer arming, signal notification, timespec validation, and selected clock support. Direct include dependencies include `unistd.h`, `signal.h`, `time.h`, `limits.h`, `tst_test.h`, `tst_safe_clocks.h`.

Risks and test signals: Timing assertions can be scheduler-sensitive, especially for short intervals or absolute time. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime03.c -->
