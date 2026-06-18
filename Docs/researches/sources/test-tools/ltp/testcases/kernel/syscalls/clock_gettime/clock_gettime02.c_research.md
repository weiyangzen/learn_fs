<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime02.c

Purpose: LTP regression coverage for `clock_gettime` behavior. Source intent: Copyright (c) 2019 Linaro Limited. Author: Rafael David Tinoco <rafael.tinoco@linaro.org> \ Bad argument tests for clock_gettime(2) on multiple clocks: #. It justifies testing EFAULT for all. The file was read in full for this report (159 lines, 3721 bytes).

Important APIs/types/functions: Primary functions are `setup`, `verify_clock_gettime`. Important call/API signals are `clock_gettime`, `tst_res`, `tst_get_bad_addr`, `tst_get_max_clocks`, `verify_clock_gettime`, `tst_ts_get`, `TEST`, `tst_clock_name`. Relevant structs/types include `struct test_case`, `struct tst_ts`, `struct time64_variants`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_clock_gettime`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"config.h"`, `"time64_variants.h"`, `"tst_timer.h"`, `"tst_safe_clocks.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `clock_gettime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EINVAL, EFAULT, CLOCK_REALTIME, CLOCK_MONOTONIC, CLOCK_PROCESS_CPUTIME_ID, CLOCK_THREAD_CPUTIME_ID, CLOCK_REALTIME_COARSE, CLOCK_MONOTONIC_COARSE, CLOCK_MONOTONIC_RAW, CLOCK_BOOTTIME`; harness fields `.test, .setup, .tcnt, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime02.c -->
