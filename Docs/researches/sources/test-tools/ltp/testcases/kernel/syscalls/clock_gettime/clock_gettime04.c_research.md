<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime04.c

Purpose: LTP regression coverage for `clock_gettime` behavior. Source intent: Copyright (c) 2020 Linaro Limited. Author: Viresh Kumar<viresh.kumar@linaro.org> \ Check time difference between successive readings and report a bug if difference found to be over 5 ms. This test reports a s390x BUG which has been fixed in kernel v5.12 in 5b43bd184530 ("s390/vdso: fix initializing and updating of vdso_data") The array defines the type to TST_LIBC_TIMESPEC and so we can cast this into struct. The file was read in full for this report (194 lines, 5074 bytes).

Important APIs/types/functions: Primary functions are `do_vdso_gettime`, `vdso_gettime`, `vdso_gettime64`, `my_gettimeofday`, `setup`, `run`. Important call/API signals are `tst_brk`, `tst_clock_name`, `tst_timespec_from_us`, `tst_timeval_to_us`, `clock_getres`, `tst_is_virt`, `tst_res`, `find_clock_gettime_vdso`, `clock_gettime`, `tst_ts_get`, `tst_ts_to_ns`. Relevant structs/types include `struct timeval`, `struct timespec`, `struct time64_variants`, `struct tst_ts`, `struct tst_tag`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.tags`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; do_-oriented functions `do_vdso_gettime`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"config.h"`, `"tse_parse_vdso.h"`, `"time64_variants.h"`, `"tst_timer.h"`, `"tst_safe_clocks.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clock_gettime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `ENOSYS, CLOCK_REALTIME, CLOCK_REALTIME_COARSE, CLOCK_MONOTONIC, CLOCK_MONOTONIC_COARSE, CLOCK_MONOTONIC_RAW, CLOCK_BOOTTIME`; harness fields `.test, .setup, .tcnt, .tags`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime04.c -->
