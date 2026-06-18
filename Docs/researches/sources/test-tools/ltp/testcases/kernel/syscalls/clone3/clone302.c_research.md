<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone302.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone302.c

Purpose: LTP regression coverage for `clone3` behavior. Source intent: Copyright (c) 2020 Viresh Kumar <viresh.kumar@linaro.org> \ Basic clone3() test to check various failures. Don't test CLONE_CHILD_SETTID and CLONE_PARENT_SETTID: When the parent tid is written to the memory location for CLONE_PARENT_SETTID we're past the point of no return of process creation, i.e. The file was read in full for this report (115 lines, 3329 bytes).

Important APIs/types/functions: Primary functions are `setup`, `run`. Important call/API signals are `clone3`, `clone3_supported_by_kernel`, `TST_EXP_EQ_SZ`, `tst_get_bad_addr`, `TEST`, `ltp_clone3_raw`, `tst_res`, `tst_strerrno`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct clone_args`, `struct tcase`, `struct clone_args_minimal`, `struct tst_buffers`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<assert.h>`, `"tst_test.h"`, `"lapi/sched.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; an isolated LTP temporary directory. It integrates with the sibling `clone3` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EFAULT, EINVAL, CLONE_SIGHAND, CLONE_THREAD, CLONE_FS, CLONE_NEWNS, CLONE_PIDFD, CLONE_CHILD_SETTID, CLONE_PARENT_SETTID`; harness fields `.test, .setup, .tcnt, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone302.c -->
