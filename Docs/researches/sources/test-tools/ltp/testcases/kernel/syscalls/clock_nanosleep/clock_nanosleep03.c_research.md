<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep03.c

Purpose: LTP regression coverage for `clock_nanosleep` behavior. Source intent: Copyright (c) 2020 Cyril Hrubis <chrubis@suse.cz> \ Test that clock_nanosleep() adds correctly an offset with absolute timeout and CLOCK_MONOTONIC inside of a timer namespace. After a call to unshare(CLONE_NEWTIME) a new timer namespace is created, the process that has called the unshare() can adjust offsets for CLOCK_MONOTONIC and CLOCK_BOOTTIME for its children by writing to the '/proc/self/timens_offsets'. The file was read in full for this report (110 lines, 3099 bytes).

Important APIs/types/functions: Primary functions are `do_clock_gettime`, `verify_clock_nanosleep`. Important call/API signals are `clock_nanosleep`, `do_clock_gettime`, `clock_gettime`, `tst_ts_get`, `tst_brk`, `clock_settime`, `verify_clock_nanosleep`, `tst_res`, `SAFE_UNSHARE`, `SAFE_FILE_PRINTF`, `tst_ts_add_us`, `SAFE_FORK`, `TEST`, `tst_clock_name`, `SAFE_WAIT`, `tst_ts_diff_us`. Defined constants/macros include `OFFSET_S`, `SLEEP_US`. Relevant structs/types include `struct time64_variants`, `struct tst_ts`. Harness metadata uses `.test_all`, `.needs_root`, `.needs_kconfigs`, `.forks_child`.

Control flow: The test is organized around verify-oriented functions `verify_clock_nanosleep`; do_-oriented functions `do_clock_gettime`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `"time64_variants.h"`, `"tst_safe_clocks.h"`, `"tst_timer.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities; kernel configuration predicates. It integrates with the sibling `clock_nanosleep` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: wall-clock mutation can affect the host if restore hooks or namespace isolation fail

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLOCK_MONOTONIC, CLONE_NEWTIME, CLOCK_BOOTTIME`; harness fields `.test_all, .needs_root, .needs_kconfigs, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_nanosleep/clock_nanosleep03.c -->
