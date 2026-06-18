<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync03.c

Purpose: Validates data persistence/metadata behavior after writing a temporary file and calling `fsync()`. Source notes: \ Verify that, fsync(2) returns -1 and sets errno to - EINVAL if calling fsync() on a pipe(fd). - EINVAL if calling fsync() on a socket(fd). - EBADF if calling fsync() on a closed fd. - EBADF if calling fsync() on an invalid fd. - EINVAL if calling fsync() on a fifo(fd). EINVAL - fsync() on pipe should not succeed. EINVAL - fsync() on socket should not succeed. EBADF - fd is closed EBADF - fd is invalid (-1) EINVAL - fsync() on fifo should not succeed. SPDX-License-Identifier: GPL-2.0-or-later // FIFO must be opened for reading first, otherwise // open(fifo, O_WRONLY) will block. // Do not open any file descriptors after this line unless you close // them before the next test run. The file was read in full for this report (89 lines, 2167 bytes).

Important APIs/types/functions: calls/wrappers: fsync(), open(), pipe(), socket(), SAFE_MKFIFO, SAFE_PIPE, SAFE_OPEN, SAFE_SOCKET, SAFE_CLOSE; types/structs: struct test_case, struct tst_test; functions: setup, test_fsync, cleanup; local macros/constants: FIFO_PATH.

Control flow: setup path: setup; exercise path: test_fsync; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `unistd.h`, `errno.h`, `tst_test.h`; integrates with the LTP fsync syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EINVAL, EBADF; key constants: O_WRONLY, O_RDONLY, O_NONBLOCK; harness metadata: .test, .tcnt, .needs_tmpdir, .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fsync/fsync03.c -->
