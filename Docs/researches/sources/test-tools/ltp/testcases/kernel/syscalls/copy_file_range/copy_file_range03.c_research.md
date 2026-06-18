<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range03.c

Purpose: LTP regression coverage for `copy_file_range` behavior. Source intent: Copyright (c) 2019 SUSE LLC Author: Christian Amann <camann@suse.com> Copies the contents of one file into another and checks if the timestamp gets updated in the process. The file was read in full for this report (82 lines, 1759 bytes).

Important APIs/types/functions: Primary functions are `verify_copy_file_range_timestamp`, `cleanup`, `setup`. Important call/API signals are `fstat`, `verify_copy_file_range_timestamp`, `TEST`, `sys_copy_file_range`, `tst_brk`, `tst_timespec_diff_us`, `tst_res`, `SAFE_CLOSE`, `syscall_info`, `SAFE_OPEN`, `SAFE_WRITE`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct timespec`, `struct stat`. Harness metadata uses `.test_all`, `.setup`, `.cleanup`, `.needs_tmpdir`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_copy_file_range_timestamp`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, kernel clock state or time namespace state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"tst_timer.h"`, `"copy_file_range.h"`; the modern LTP `struct tst_test` harness; an isolated LTP temporary directory. It integrates with the sibling `copy_file_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: filesystem, cross-device, immutable, swapfile, and special-file behavior varies by kernel and backing fs

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `O_RDWR, O_CREAT, O_RDONLY`; harness fields `.test_all, .setup, .cleanup, .needs_tmpdir`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range03.c -->
