# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod01.c

Purpose: Verify that mknod(2) successfully creates a filesystem node with various modes.

Important APIs/types/functions: mknod, unlink, tst_test, TST_EXP_PASS, SAFE_UNLINK; local functions detected: run; key constants/macros: PATH

Control flow: test iterates over the testcase table. Local helper functions: run.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: TST_EXP_PASS success assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
