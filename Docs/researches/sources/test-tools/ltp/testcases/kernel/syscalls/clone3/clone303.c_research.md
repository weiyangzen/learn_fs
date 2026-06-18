<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone303.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone303.c

Purpose: LTP regression coverage for `clone3` behavior. Source intent: Copyright (c) 2023 SUSE LLC <wegao@suse.com> \ This test case check clone3 CLONE_INTO_CGROUP flag The file was read in full for this report (93 lines, 1660 bytes).

Important APIs/types/functions: Primary functions are `clone_into_cgroup`, `run`, `setup`, `cleanup`. Important call/API signals are `clone_into_cgroup`, `tst_clone`, `TST_CHECKPOINT_WAIT`, `SAFE_CG_READ`, `tst_res`, `tst_brk`, `clone3`, `TST_CHECKPOINT_WAKE`, `SAFE_WAITPID`, `clone3_supported_by_kernel`, `tst_cg_group_mk`, `tst_cg_group_unified_dir_fd`, `tst_cg_group_rm`. Defined constants/macros include `_GNU_SOURCE`, `BUF_LEN`. Relevant structs/types include `struct tst_cg_group`, `struct tst_clone_args`, `struct tst_buffers`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_checkpoints`, `.forks_child`, `.min_kver`.

Control flow: The test is organized around setup-oriented functions `setup`; run-oriented functions `run`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, child processes and exit status. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `<stdlib.h>`, `<sys/wait.h>`, `"tst_test.h"`, `"lapi/sched.h"`, `"lapi/pidfd.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `clone3` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: clone flag semantics are architecture- and kernel-version-sensitive

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `CLONE_INTO_CGROUP`; harness fields `.test_all, .setup, .cleanup, .needs_checkpoints, .forks_child, .min_kver`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/clone3/clone303.c -->
