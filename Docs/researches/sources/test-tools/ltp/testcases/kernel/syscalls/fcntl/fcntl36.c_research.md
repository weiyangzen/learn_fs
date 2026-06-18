<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl36.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl36.c

Purpose: OFD lock concurrency stress test comparing OFD and POSIX locking behavior across threaded readers/writers and validating final file contents. Source notes: Author: Xiong Zhou <xzhou@redhat.com> This is testing OFD locks racing with POSIX locks: OFD read lock vs OFD write lock OFD read lock vs POSIX write lock OFD write lock vs POSIX write lock OFD write lock vs POSIX read lock OFD write lock vs OFD write lock OFD r/w locks vs POSIX write locks OFD r/w locks vs POSIX read locks For example: Init an file with preset values. Threads acquire OFD READ locks to read a 4k section start from 0; checking data read back, there should not be any surprise values and data should be consistent in a 1k block. Threads acquire OFD WRITE locks to write a 4k section start from 1k, writing different values in different threads. Check file data after racing, there should not be any surprise values and data should be consistent in a 1k block. OFD write lock writing data POSIX write lock writing data SPDX-Licen... The file was read in full for this report (395 lines, 8364 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_OPEN, SAFE_LSEEK, SAFE_WRITE, SAFE_CLOSE, SAFE_FCNTL, SAFE_READ, SAFE_PTHREAD_CREATE, SAFE_PTHREAD_JOIN; types/structs: struct param, struct flock, struct tcase, struct tst_test; functions: setup, fn_ofd_w, fn_posix_w, fn_ofd_r, fn_posix_r, fn_dummy, test_fn, tests.

Control flow: setup path: setup; exercise path: fn_ofd_w, fn_posix_w, fn_ofd_r, fn_posix_r, fn_dummy, test_fn, tests; notable execution mechanics: iterates a case table, uses pthread workers for concurrent access.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, threads and shared in-process synchronization, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `unistd.h`, `stdio.h`, `stdlib.h`, `pthread.h`, `sched.h`, `errno.h`, `lapi/fcntl.h`, `tst_safe_pthread.h`, `tst_test.h`, `fcntl_common.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: O_RDWR, F_WRLCK, F_OFD_SETLKW, F_UNLCK, F_SETLKW, F_RDLCK, F_OFD_SETLK, F_SETLK, O_RDONLY; harness metadata: .timeout, .needs_tmpdir, .test, .tcnt, .setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl36.c -->
