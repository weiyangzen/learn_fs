# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod07.c

Purpose: Verify that mknod(2) fails with the correct error codes: - EACCES if parent directory does not allow write permission to the process. - EPERM if the process id of the caller is not super-user. - EROFS if pathname refers to a file on a read-only file system. - ELOOP if too many symbolic links were encountered in resolving pathname.

Important APIs/types/functions: mknod, mkdir, symlink, seteuid, tst_test, TST_EXP_FAIL, SAFE_GETPWNAM, SAFE_SETEUID, SAFE_MKDIR, SAFE_SYMLINK, tst_buffers; local functions detected: run, setup; key constants/macros: TEMP_MNT, TEMP_DIR, TEMP_DIR_MODE, ELOOP_DIR, ELOOP_FILE, ELOOP_DIR_MODE, ELOOP_MAX, FIFO_MODE, SOCKET_MODE, CHR_MODE, BLK_MODE, TEST_SIZE

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: run, setup.

State and persistence behavior: procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; mount/device availability and filesystem semantics affect read-only and node-creation cases; requires a usable nobody account and predictable privilege transitions.

Test signals: TST_EXP_FAIL errno assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: The kernel limits symlink resolution hop amount to 40, create a pathname with more than that
