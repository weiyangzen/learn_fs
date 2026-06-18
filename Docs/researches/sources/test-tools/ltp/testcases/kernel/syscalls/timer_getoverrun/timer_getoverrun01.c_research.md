<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_getoverrun/timer_getoverrun01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_getoverrun/timer_getoverrun01.c

Purpose: Porting from Crackerjack to LTP is done by: Manas Kumar Nayak <maknayak@in.ibm.com> This test checks base timer_getoverrun() functionality.

Important APIs/types/functions: includes `signal.h`, `time.h`, `tst_safe_clocks.h`, `lapi/syscalls.h`, `lapi/common_timers.h`; exercises `time`, `timer_create`, `timer_delete`, `timer_getoverrun`, `raw syscall path`; defines `run`; uses constants `CLOCK_REALTIME`, `EINVAL`, `SIGALRM`, `SIGEV_SIGNAL`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is POSIX timer signal overrun accounting after an interval timer expires faster than signals are consumed.

Dependencies and integration points: Depends on POSIX interval timers, signal blocking/handling, and kernel overrun accounting limits. Direct include dependencies include `signal.h`, `time.h`, `tst_safe_clocks.h`, `lapi/syscalls.h`, `lapi/common_timers.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TST_EXP_FAIL`, `TST_EXP_POSITIVE`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_getoverrun/timer_getoverrun01.c -->
