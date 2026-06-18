# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod09.c

Purpose: Verify that mknod() fails with -1 and sets errno to EINVAL if the mode is different than a normal file, device special file or FIFO.

Important APIs/types/functions: mknod, tst_test, TST_EXP_FAIL; local functions detected: check_mknod; key constants/macros: No prominent local constants beyond included headers.

Control flow: test_all runs one whole-file scenario. Local helper functions: check_mknod.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: TST_EXP_FAIL errno assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
