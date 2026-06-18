# sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat02.c

Purpose: This test verifies that: 1) lstat(2) returns -1 and sets errno to EACCES if search permission is denied on a component of the path prefix. 2) lstat(2) returns -1 and sets errno to ENOENT if the specified file does not exists or empty string. 3) lstat(2) returns -1 and sets errno to EFAULT if pathname points outside user's accessible address space. 4) lstat(2) returns -1 and sets errno to ENAMETOOLONG if the pathname component is too long. 5) lstat(2) returns -1 and sets errno to ENOTDIR if the directory component in pathname is not a directory. 6) lstat(2) returns -1 and sets errno to ELOOP if the pathname has too many symbolic links encou...

Important APIs/types/functions: mkdir, lstat, symlink, seteuid, memset, tst_test, TST_RET, tst_res, TST_ERR, tst_strerrno, SAFE_GETPWNAM, SAFE_SETEUID, SAFE_MKDIR, SAFE_TOUCH, SAFE_CHMOD, SAFE_SYMLINK; local functions detected: run, setup, cleanup; key constants/macros: MODE_RWX, MODE_RW0, TEST_DIR, TEST_FILE, TEST_ELOOP, TEST_ENOENT, TEST_EACCES, TEST_ENOTDIR

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: run, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; requires a usable nobody account and predictable privilege transitions.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Drop privileges for EACCES test NOTE: The ELOOP test is written based on the fact that the consecutive symlinks limit in the kernel is hardwired to 40.
