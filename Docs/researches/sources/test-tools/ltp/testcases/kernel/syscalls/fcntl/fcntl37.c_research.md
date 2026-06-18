<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl37.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl37.c

Purpose: Negative pipe-size test for `F_SETPIPE_SZ`, including too-small, too-large, and over-capacity values. Source notes: Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com> Test basic error handling for fcntl(2) using F_SETPIPE_SZ, F_GETPIPE_SZ argument. 1)fcntl fails with EINVAL when cmd is F_SETPIPE_SZ and the arg is beyond 1<<31. 2)fcntl fails with EBUSY when cmd is F_SETPIPE_SZ and the arg is smaller than the amount of the current used buffer space. 3)fcntl fails with EPERM when cmd is F_SETPIPE_SZ and the arg is over /proc/sys/fs/pipe-max-size limit under unprivileged users. SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (97 lines, 2451 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_PIPE, SAFE_MALLOC, SAFE_WRITE, SAFE_FILE_SCANF, SAFE_CLOSE, TST_CAP; types/structs: struct tcase, struct tst_test, struct tst_cap; functions: verify_fcntl, setup, cleanup.

Control flow: setup path: setup; exercise path: verify_fcntl; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, kernel tunables that setup/cleanup must restore, UID/capability-sensitive kernel state, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `unistd.h`, `sys/types.h`, `limits.h`, `stdlib.h`, `tst_test.h`, `lapi/fcntl.h`, `lapi/capability.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: must restore proc/sys tunables after failures.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL, EBUSY, EPERM; key constants: F_SETPIPE_SZ, F_GETPIPE_SZ, F_GET, PATH_FS_PIPE_MAX_SIZE; harness metadata: .setup, .cleanup, .tcnt, .test.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl37.c -->
