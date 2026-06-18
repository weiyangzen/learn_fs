<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module02.c

Purpose: LTP regression coverage for `delete_module` behavior. Source intent: Copyright (c) Wipro Technologies Ltd, 2002. Copyright (c) 2018 Xiao Yang <yangx.jy@cn.fujitsu.com> AUTHOR: Madhu T L <madhu.tarikere@wipro.com> DESCRIPTION Verify that, 1. delete_module(2) returns -1 and sets errno to ENOENT for nonexistent module entry. delete_module(2) returns -1 and sets errno to EFAULT, if module name parameter is outside program's accessible address space. The file was read in full for this report (97 lines, 2524 bytes).

Important APIs/types/functions: Primary functions are `do_delete_module`, `setup`. Important call/API signals are `delete_module`, `do_delete_module`, `tst_get_bad_addr`, `SAFE_SETEUID`, `tst_res`, `TEST`, `tst_syscall`, `tst_strerrno`, `SAFE_GETPWNAM`. Defined constants/macros include `BASEMODNAME`, `LONGMODNAMECHAR`, `MODULE_NAME_LEN`. Relevant structs/types include `struct passwd`, `struct test_case_t`. Harness metadata uses `.test`, `.setup`, `.tcnt`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; do_-oriented functions `do_delete_module`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates child processes and exit status, loadable kernel module state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<errno.h>`, `<pwd.h>`, `<stdio.h>`, `<string.h>`, `"tst_test.h"`, `"lapi/syscalls.h"`; the modern LTP `struct tst_test` harness; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps; root privileges or selected Linux capabilities. It integrates with the sibling `delete_module` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: module loading/removal requires root and can be blocked by kernel lockdown, taint policy, or module dependencies

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `ENOENT, EFAULT, EPERM`; harness fields `.test, .setup, .tcnt, .needs_root`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/delete_module02.c -->
