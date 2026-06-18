<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl34.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl34.c

Purpose: Open-file-description lock write test that uses multiple pthreads to append patterned data safely under OFD locks. Source notes: Author: Alexey Kodanev <alexey.kodanev@oracle.com> SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (131 lines, 2642 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_PTHREAD_CREATE, SAFE_PTHREAD_JOIN, SAFE_OPEN, SAFE_LSEEK, SAFE_WRITE, SAFE_CLOSE, SAFE_READ; types/structs: struct flock, struct tst_test; functions: setup, spawn_threads, wait_threads, thread_fn_01, test01.

Control flow: setup path: setup; exercise path: thread_fn_01, test01; notable execution mechanics: uses pthread workers for concurrent access.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, threads and shared in-process synchronization, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `unistd.h`, `pthread.h`, `sched.h`, `fcntl_common.h`, `tst_safe_pthread.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, F_WRLCK, F_OFD_SETLKW, F_UNLCK, O_CREAT, O_TRUNC; harness metadata: .needs_tmpdir, .test_all, .setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl34.c -->
