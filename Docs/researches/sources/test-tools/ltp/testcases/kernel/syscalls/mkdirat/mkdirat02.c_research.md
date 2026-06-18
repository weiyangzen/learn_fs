# sources/test-tools/ltp/testcases/kernel/syscalls/mkdirat/mkdirat02.c

Purpose: DESCRIPTION check mkdirat() with various error conditions that should produce ELOOP and EROFS.

Important APIs/types/functions: open, mkdir, mkdirat, symlink, tst_test, SAFE_OPEN, SAFE_MKDIR, SAFE_SYMLINK, TST_RET, tst_res, TST_ERR, tst_strerrno; local functions detected: setup, mkdirat_verify; key constants/macros: MNT_POINT, TEST_DIR, DIR_MODE

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: setup, mkdirat_verify.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: NOTE: the ELOOP test is written based on that the consecutive symlinks limits in kernel is hardwired to 40.
