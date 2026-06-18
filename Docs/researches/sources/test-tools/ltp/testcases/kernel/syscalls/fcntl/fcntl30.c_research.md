<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl30.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl30.c

Purpose: Validates `F_GETPIPE_SZ` and `F_SETPIPE_SZ` on a pipe using `/proc/sys/fs/pipe-max-size` as the unprivileged maximum. Source notes: Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com> \ Verify that, fetching and changing the capacity of a pipe works as expected with fcntl(2) syscall using F_GETPIPE_SZ, F_SETPIPE_SZ arguments. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (52 lines, 1127 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_PIPE, TST_EXP_POSITIVE, TST_EXP_EXPR, SAFE_CLOSE, SAFE_FILE_SCANF; types/structs: struct tst_test; functions: run, setup, cleanup.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates UID/capability-sensitive kernel state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/fcntl.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: key constants: F_GETPIPE_SZ, F_SETPIPE_SZ, PATH_FS_PIPE_MAX_SIZE; harness metadata: .test_all, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl30.c -->
