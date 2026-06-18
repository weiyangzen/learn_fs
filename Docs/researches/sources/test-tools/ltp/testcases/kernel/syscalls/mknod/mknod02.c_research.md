# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod02.c

Purpose: Verify that if mknod(2) creates a filesystem node in a directory which does not have the set-group-ID bit set, new node will not inherit the group ownership from its parent directory and its group ID will be the effective group ID of the process.

Important APIs/types/functions: mknod, mkdir, stat, unlink, tst_test, SAFE_GETPWNAM, SAFE_MKDIR, SAFE_CHOWN, TST_EXP_PASS, SAFE_STAT, TST_EXP_EQ_LI, SAFE_UNLINK; local functions detected: setup, run; key constants/macros: MODE_DIR, MODE1, MODE_SGID, TEMP_DIR, TEMP_NODE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: setup, run.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: requires a usable nobody account and predictable privilege transitions.

Test signals: TST_EXP_PASS success assertions; TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
