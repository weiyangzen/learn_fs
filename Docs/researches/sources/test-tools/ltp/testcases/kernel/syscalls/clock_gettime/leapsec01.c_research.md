<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/leapsec01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/leapsec01.c

Purpose: LTP regression coverage for `clock_gettime` behavior. Source intent: Copyright (c) Red Hat, Inc., 2012. Copyright (c) Linux Test Project, 2019 Author: Lingzhu Xiang <lxiang@redhat.com> Ported to new library: 07/2019 Christian Amann <camann@suse.com> \ Regression test for hrtimer early expiration during and after leap seconds A bug in the hrtimer subsystem caused all TIMER_ABSTIME CLOCK_REALTIME timers to expire one second early during leap second. The file was read in full for this report (206 lines, 5049 bytes).

Important APIs/types/functions: Primary functions are `in_order`, `adjtimex_status`, `test_hrtimer_early_expiration`, `run_leapsec`, `setup`, `cleanup`. Important call/API signals are `adjtimex_status`, `tst_brk`, `tst_res`, `test_hrtimer_early_expiration`, `SAFE_CLOCK_GETTIME`, `clock_nanosleep`, `SAFE_CLOCK_SETTIME`, `clock_was_set`. Defined constants/macros include `SECONDS_BEFORE_LEAP`, `SECONDS_AFTER_LEAP`. Relevant structs/types include `struct timespec`, `struct timex`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run_leapsec`; test-oriented functions `test_hrtimer_early_expiration`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<sys/types.h>`, `<errno.h>`, `<stdio.h>`, `<time.h>`, `"tst_test.h"`, `"tst_safe_clocks.h"`, `"lapi/common_timers.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `clock_gettime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: wall-clock mutation can affect the host if restore hooks or namespace isolation fail

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EPERM, CLOCK_REALTIME, CLOCK_MONOTONIC`; harness fields `.test_all, .setup, .cleanup, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/leapsec01.c -->
