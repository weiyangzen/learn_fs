<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock02.c

Purpose: Checks nonblocking `flock()` conflict behavior and expected `EWOULDBLOCK`/`EAGAIN` style failures. Source notes: Author: Vatsal Avasthi \ Verify flock(2) returns -1 and set proper errno: - EBADF if the file descriptor is invalid - EINVAL if the argument operation does not include LOCK_SH,LOCK_EX,LOCK_UN - EINVAL if an invalid combination of locking modes is used i.e LOCK_SH with LOCK_EX - EWOULDBLOCK if the file is locked and the LOCK_NB flag was selected SPDX-License-Identifier: GPL-2.0-or-later The file was read in full for this report (80 lines, 1746 bytes).

Important APIs/types/functions: calls/wrappers: flock(), SAFE_OPEN, SAFE_CLOSE; types/structs: struct tcase, struct tst_test; functions: verify_flock, setup.

Control flow: setup path: setup; exercise path: verify_flock; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, temporary mount/test filesystem state, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `sys/file.h`, `tst_test.h`; integrates with the LTP flock syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBADF, EINVAL, EWOULDBLOCK; key constants: LOCK_SH, LOCK_EX, LOCK_UN, LOCK_NB, O_RDWR, O_CREAT, O_TRUNC; harness metadata: .tcnt, .test, .needs_tmpdir, .setup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/flock/flock02.c -->
