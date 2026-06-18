<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep02.c

Purpose: LTP regression coverage for `clock_nanosleep` behavior. Source intent: Copyright (C) 2017 Cyril Hrubis <chrubis@suse.cz> Test Description: clock_nanosleep() should return with value 0 and the process should be suspended for time specified by timespec structure. The file was read in full for this report (37 lines, 727 bytes).

Important APIs/types/functions: Primary functions are `sample_fn`. Important call/API signals are `clock_nanosleep`, `tst_timespec_from_us`, `tst_timer_start`, `TEST`, `tst_timer_stop`, `tst_timer_sample`, `tst_res`. Relevant structs/types include `struct timespec`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around entry/helper functions `sample_fn`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates kernel clock state or time namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `"tst_timer_test.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `clock_nanosleep` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TFAIL/TST_EXP_FAIL failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep02.c -->
