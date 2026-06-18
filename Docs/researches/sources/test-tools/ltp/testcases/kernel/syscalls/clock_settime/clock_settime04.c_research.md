<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime04.c

Purpose: LTP regression coverage for `clock_settime` behavior. Source intent: Copyright (c) 2025 Andrea Cervesato <andrea.cervesato@suse.com> \ Verify that changing the value of the CLOCK_REALTIME clock via clock_settime() shall have no effect on a thread that is blocked on absolute/relative clock_nanosleep(). The file was read in full for this report (137 lines, 3340 bytes).

Important APIs/types/functions: Primary functions are `child_nanosleep`, `run`, `setup`. Important call/API signals are `clock_settime`, `clock_nanosleep`, `SAFE_CLOCK_GETTIME`, `tst_res`, `tst_ts_set_sec`, `tst_ts_set_nsec`, `tst_ts_add_us`, `tst_ts_from_us`, `TEST`, `tst_ts_get`, `tst_brk`, `tst_timespec_lt`, `tst_timespec_to_ms`, `tst_timespec_abs_diff_us`, `SAFE_FORK`, `SAFE_CLOCK_NANOSLEEP`, `SAFE_CLOCK_SETTIME`. Defined constants/macros include `SEC_TO_US`, `CHILD_SLEEP_US`, `PARENT_SLEEP_S`, `DELTA_US`. Relevant structs/types include `struct tst_ts`, `struct time64_variants`, `struct timespec`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`, `.forks_child`, `.restore_wallclock`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; child-oriented functions `child_nanosleep`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"tst_timer.h"`, `"tst_safe_clocks.h"`, `"time64_variants.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `clock_settime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: wall-clock mutation can affect the host if restore hooks or namespace isolation fail

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLOCK_REALTIME, CLOCK_MONOTONIC`; harness fields `.test, .setup, .tcnt, .needs_root, .forks_child, .restore_wallclock`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_settime/clock_settime04.c -->
