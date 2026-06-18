<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range02.c

Purpose: LTP regression coverage for `copy_file_range` behavior. Source intent: Copyright (c) 2019 SUSE LLC Author: Christian Amann <camann@suse.com> Tests basic error handling of the copy_file_range syscall 1) Try to copy contents to file open as readonly -> EBADF 2) Try to copy contents to directory -> EISDIR 3) Try to copy contents to a file opened with the O_APPEND flag -> EBADF 4) Try to copy contents to closed file descriptor -> EBADF 5) Try to copy contents with invalid 'flags' value ->. The file was read in full for this report (257 lines, 6991 bytes).

Important APIs/types/functions: Primary functions are `run_command`, `verify_copy_file_range`, `cleanup`, `setup`. Important call/API signals are `tst_cmd`, `tst_res`, `verify_copy_file_range`, `copy_file_range`, `tst_max_lfs_filesize`, `TEST`, `sys_copy_file_range`, `tst_strerrno`, `SAFE_CLOSE`, `SAFE_UNLINK`, `syscall_info`, `SAFE_MKDIR`, `tst_find_free_loopdev`, `SAFE_MKNOD`, `SAFE_OPEN`, `SAFE_PIPE`, `SAFE_WRITE`, `close`, `tst_fs_has_free`, `tst_fill_file`. Defined constants/macros include `_GNU_SOURCE`. Relevant structs/types include `struct tcase`. Harness metadata uses `.test`, `.setup`, `.cleanup`, `.tcnt`, `.needs_root`.

Control flow: The test is organized around setup-oriented functions `setup`; verify-oriented functions `verify_copy_file_range`; run-oriented functions `run_command`; cleanup-oriented functions `cleanup`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects, pollable descriptor readiness state, effective UID/GID or Linux capability state. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `"tst_test.h"`, `"copy_file_range.h"`; the modern LTP `struct tst_test` harness; root privileges or selected Linux capabilities. It integrates with the sibling `copy_file_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: filesystem, cross-device, immutable, swapfile, and special-file behavior varies by kernel and backing fs

Test signals: explicit TPASS/TST_EXP_PASS success paths; explicit TFAIL/TST_EXP_FAIL failure paths; case/errno constants `EBADF, EISDIR, EINVAL, EPERM, ETXTBSY, EOVERFLOW, EFBIG, O_APPEND, F_OK, O_RDWR, O_CREAT, O_RDONLY, O_DIRECTORY, O_WRONLY, O_TRUNC`; harness fields `.test, .setup, .cleanup, .tcnt, .needs_root`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range02.c -->
