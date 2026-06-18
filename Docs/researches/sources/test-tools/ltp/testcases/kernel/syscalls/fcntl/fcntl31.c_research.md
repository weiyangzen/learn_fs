<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl31.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl31.c

Purpose: Comprehensive asynchronous I/O owner/signal test for `F_SETOWN`, `F_GETOWN`, `F_SETOWN_EX`, `F_GETOWN_EX`, `F_SETSIG`, and `F_GETSIG`. Source notes: Author: Xiaoguang Wang <wangxg.fnst@cn.fujitsu.com> This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. You should have received a copy of the GNU General Public License along with this program; if not, write the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA. Description: Verify that: Basic test for fcntl(2) using F_GETOWN, F_SETOWN, F_GETOWN_EX, F_SETOWN_EX, F_GETSIG, F_SETSIG argument. we have these tests on pipe Changing process group ID is forbidden when PID == SID i.e. we are sessio... The file was read in full for this report (361 lines, 8287 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), wait(), close(), write(), SAFE_PIPE, SAFE_READ; types/structs: struct f_owner_ex, struct timespec; functions: main, setup, setown_pid_test, setown_pgrp_test, setownex_cleanup, setownex_tid_test, setownex_pid_test, setownex_pgrp_test, test_set_and_get_sig, signal_parent, check_io_signal, cleanup.

Control flow: setup path: setup; exercise path: main, setown_pid_test, setown_pgrp_test, setownex_tid_test, setownex_pid_test, setownex_pgrp_test, test_set_and_get_sig, signal_parent; cleanup path: setownex_cleanup, cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `stdio.h`, `errno.h`, `unistd.h`, `string.h`, `signal.h`, `sys/types.h`, `sys/wait.h`, `pwd.h`, `sched.h`, `test.h`, `config.h`, `lapi/syscalls.h`, `tso_safe_macros.h`, `lapi/fcntl.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: F_GETOWN, F_SETOWN, F_GETOWN_EX, F_SETOWN_EX, F_GETSIG, F_SETSIG, F_SETFL, O_ASYNC, SIGUSR1, SIGIO, F_OWNER_TID, __NR_gettid.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl31.c -->
