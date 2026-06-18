<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep04.c

Purpose: LTP regression coverage for `clock_nanosleep` behavior. Source intent: Copyright (c) M. Koehrer <mathias_koehrer@arcor.de>, 2009 Copyright (C) 2017 Cyril Hrubis <chrubis@suse.cz> The file was read in full for this report (67 lines, 1892 bytes).

Important APIs/types/functions: Primary functions are `setup`, `do_test`. Important call/API signals are `tst_res`, `TEST`, `clock_gettime`, `tst_ts_get`, `tst_clock_name`, `tst_ts_add_us`, `clock_nanosleep`. Relevant structs/types include `struct time64_variants`, `struct tst_ts`. Harness metadata uses `.test`, `.setup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; test-oriented functions `do_test`; do_-oriented functions `do_test`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<time.h>`, `<unistd.h>`, `"time64_variants.h"`, `"tst_safe_clocks.h"`, `"tst_timer.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clock_nanosleep` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLOCK_MONOTONIC, CLOCK_REALTIME`; harness fields `.test, .setup, .tcnt`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep04.c -->
