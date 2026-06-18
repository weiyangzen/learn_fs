<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime03.c

Purpose: LTP regression coverage for `clock_gettime` behavior. Source intent: Copyright (c) 2020 Cyril Hrubis <chrubis@suse.cz> \ After a call to unshare(CLONE_NEWTIME) a new timer namespace is created, the process that has called the unshare() can adjust offsets for CLOCK_MONOTONIC and CLOCK_BOOTTIME for its children by writing to the '/proc/self/timens_offsets'. The file was read in full for this report (143 lines, 3736 bytes).

Important APIs/types/functions: Primary functions are `child`, `verify_ns_clock`, `setup`, `cleanup`. Important call/API signals are `clock_gettime`, `tst_ts_get`, `tst_res`, `tst_clock_name`, `SAFE_SETNS`, `tst_ts_diff_ms`, `verify_ns_clock`, `SAFE_UNSHARE`, `SAFE_FILE_PRINTF`, `SAFE_FORK`, `tst_is_virt`, `SAFE_OPEN`, `SAFE_CLOSE`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct tcase`, `struct tst_ts`, `struct time64_variants`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_root`, `.needs_kconfigs`, `.forks_child`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_ns_clock`; cleanup-oriented functions `cleanup`; child-oriented functions `child`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status, kernel clock state or time namespace state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"time64_variants.h"`, `"tst_safe_clocks.h"`, `"tst_timer.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities; kernel configuration predicates. It integrates with the sibling `clock_gettime` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: expected errno and return-value assertions are sensitive to kernel, libc, and architecture ABI differences

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLONE_NEWTIME, CLOCK_MONOTONIC, CLOCK_BOOTTIME, CLOCK_MONOTONIC_RAW, CLOCK_MONOTONIC_COARSE, O_RDONLY`; harness fields `.test, .setup, .cleanup, .tcnt, .needs_root, .needs_kconfigs, .forks_child`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clock_gettime/clock_gettime03.c -->
