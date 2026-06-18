<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range01.c

Purpose: LTP regression coverage for `copy_file_range` behavior. Source intent: Copyright (c) Linux Test Project, 2019 This tests the fundamental functionalities of the copy_file_range syscall. It does so by copying the contents of one file into another using various different combinations for length and input/output offsets. After a copy is done this test checks if the contents of both files are equal at the given offsets. The file was read in full for this report (237 lines, 5511 bytes).

Important APIs/types/functions: Primary functions are `check_file_content`, `check_file_offset`, `test_one`, `open_files`, `close_files`, `copy_file_range_verify`, `setup`, `cleanup`. Important call/API signals are `SAFE_FOPEN`, `tst_brk`, `SAFE_FCLOSE`, `SAFE_LSEEK`, `tst_res`, `copy_file_range`, `TEST`, `sys_copy_file_range`, `open_files`, `SAFE_OPEN`, `close_files`, `SAFE_CLOSE`, `copy_file_range_verify`, `syscall_info`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `copy_file_range_verify`; test-oriented functions `test_one`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"tst_safe_stdio.h"`, `"copy_file_range.h"`; the modern LTP `struct tst_test` harness. It integrates with the sibling `copy_file_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: filesystem, cross-device, immutable, swapfile, and special-file behavior varies by kernel and backing fs

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `O_RDONLY, O_CREAT, O_WRONLY, O_TRUNC`; harness fields `.test, .setup, .cleanup, .tcnt`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range01.c -->
