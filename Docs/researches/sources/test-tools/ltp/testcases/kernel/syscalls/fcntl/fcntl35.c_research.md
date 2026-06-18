<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl35.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl35.c

Purpose: Pipe capacity privilege regression test proving unprivileged users cannot exceed `/proc/sys/fs/pipe-max-size` while privileged paths can use larger pipe sizes. Source notes: Author: Xiao Yang <yangx.jy@cn.fujitsu.com> Description: fcntl(2) manpage states that an unprivileged user could not set the pipe capacity above the limit in /proc/sys/fs/pipe-max-size. However, an unprivileged user could create a pipe whose initial capacity exceeds the limit. We add a regression test to check that pipe-max-size caps the initial allocation for a new pipe for unprivileged users, but not for privileged users. This kernel bug has been fixed by: commit 086e774a57fba4695f14383c0818994c0b31da7c Author: Michael Kerrisk (man-pages) <mtk.manpages@gmail.com> Date: Tue Oct 11 13:53:43 2016 -0700 pipe: cap initial pipe capacity according to pipe-max-size limit SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (124 lines, 2783 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), SAFE_FILE_SCANF, SAFE_FILE_PRINTF, SAFE_GETPWNAM, SAFE_PIPE, SAFE_CLOSE, SAFE_FORK, SAFE_SETUID; types/structs: struct passwd, struct tcase, struct tst_test, struct tst_tag; functions: setup, cleanup, verify_pipe_size, do_test.

Control flow: setup path: setup; exercise path: verify_pipe_size, do_test; cleanup path: cleanup; notable execution mechanics: iterates a case table, forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status, kernel tunables that setup/cleanup must restore, UID/capability-sensitive kernel state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/types.h`, `pwd.h`, `unistd.h`, `stdlib.h`, `lapi/fcntl.h`, `tst_test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: requires root/capability-sensitive behavior; must restore proc/sys tunables after failures; scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: PATH_FS_PIPE_MAX_SIZE, F_OK, F_GETPIPE_SZ; harness metadata: .needs_root, .forks_child, .tcnt, .setup, .cleanup, .test, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl35.c -->
