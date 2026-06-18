<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range.h

Purpose: Shared helper/header support for the LTP copy_file_range tests. Source intent: Copyright (c) 2019 SUSE LLC Author: Christian Amann <camann@suse.com> Writing page_size * 4 of data into test file __COPY_FILE_RANGE_H__ else The file was read in full for this report (83 lines, 2035 bytes).

Important APIs/types/functions: Primary functions are `syscall_info`, `sys_copy_file_range`, `verify_cross_fs_copy_support`. Important call/API signals are `syscall_info`, `tst_res`, `copy_file_range`, `sys_copy_file_range`, `tst_brk`, `tst_syscall`, `SAFE_OPEN`, `SAFE_WRITE`, `TEST`, `SAFE_CLOSE`. Defined constants/macros include `__COPY_FILE_RANGE_H__`, `TEST_VARIANTS`, `MNTPOINT`, `FILE_SRC_PATH`, `FILE_DEST_PATH`, `FILE_RDONL_PATH`, `FILE_DIR_PATH`, `FILE_MNTED_PATH`, `FILE_IMMUTABLE_PATH`, `FILE_SWAP_PATH`, `FILE_CHRDEV`, `FILE_FIFO`, `FILE_COPY_PATH`, `CONTENT`, `CONTSIZE`, `MIN_OFF`. The file has little or no explicit LTP harness metadata.

Control flow: The test is organized around verify-oriented functions `verify_cross_fs_copy_support`. Setup prepares the descriptors, credentials, clocks, modules, sockets, or buffers needed by the case table; the run/verify path invokes the target syscall or wrapper; cleanup closes descriptors and restores temporary state.

State and persistence behavior: The test manipulates file descriptors and temporary filesystem objects. Persistent host changes are intended to be limited to temporary files, temporary descriptors, child processes, or explicitly restored kernel state.

Dependencies and integration points: It depends on headers `<stdio.h>`, `"lapi/syscalls.h"`, `"lapi/fs.h"`; LTP `lapi` compatibility wrappers for kernel/libc ABI gaps. It integrates with the sibling `copy_file_range` syscall suite and the LTP result model (`TPASS`, `TFAIL`, `TBROK`, `TCONF`).

Risks: filesystem, cross-device, immutable, swapfile, and special-file behavior varies by kernel and backing fs

Test signals: case/errno constants `EXDEV, O_RDWR, O_CREAT`; TCONF skip paths for unsupported kernel, libc, privilege, device, or filesystem conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/copy_file_range/copy_file_range.h -->
