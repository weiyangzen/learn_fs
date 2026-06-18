<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module03.c

Purpose: LTP regression coverage for `delete_module` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2018 Xiao Yang <yangx.jy@cn.fujitsu.com> AUTHOR: Madhu T L <madhu.tarikere@wipro.com> DESCRIPTION Verify that, delete_module(2) returns -1 and sets errno to EWOULDBLOCK, if tried to remove a module while other modules depend on this module. The file was read in full for this report (85 lines, 2029 bytes).

Important APIs/types/functions: Primary functions are `do_delete_module`, `setup`, `cleanup`. Important call/API signals are `delete_module`, `do_delete_module`, `TEST`, `tst_syscall`, `tst_res`, `tst_strerrno`, `tst_module_load`, `tst_requires_module_signature_disabled`, `tst_module_unload`. Defined constants/macros include `DUMMY_MOD`, `DUMMY_MOD_KO`, `DUMMY_MOD_DEP_KO`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; cleanup-oriented functions `cleanup`; do_-oriented functions `do_delete_module`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates loadable kernel module state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdlib.h>`, `<errno.h>`, `"tst_test.h"`, `"tst_module.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `delete_module` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: module loading/removal requires root and can be blocked by kernel lockdown, taint policy, or module dependencies

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EWOULDBLOCK`; harness fields `.test_all, .setup, .cleanup, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module03.c -->
