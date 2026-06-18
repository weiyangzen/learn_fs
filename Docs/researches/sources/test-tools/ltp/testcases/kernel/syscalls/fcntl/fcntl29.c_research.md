<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl29.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl29.c

Purpose: Verifies `F_DUPFD_CLOEXEC` duplicates a descriptor and sets `FD_CLOEXEC` on the new descriptor. Source notes: Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com> \ Basic test for fcntl(2) using F_DUPFD_CLOEXEC and getting FD_CLOEXEC. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (47 lines, 905 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_CREAT, SAFE_CLOSE, TST_EXP_FD, TST_EXP_POSITIVE; types/structs: struct tst_test; functions: setup, cleanup, run.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `lapi/fcntl.h`, `tst_test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: F_DUPFD_CLOEXEC, F_GETFD; harness metadata: .test_all, .setup, .cleanup, .needs_tmpdir.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl29.c -->
