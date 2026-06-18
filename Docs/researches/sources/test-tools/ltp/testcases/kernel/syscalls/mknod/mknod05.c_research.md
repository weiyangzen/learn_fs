# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod05.c

Purpose: Verify that mknod(2) succeeds when used to create a filesystem node with set-group-ID bit set on a directory with set-group-ID bit set. The node created should have set-group-ID bit set and its gid should be equal to that of its parent directory.

Important APIs/types/functions: mknod, mkdir, stat, unlink, tst_uid, tst_test, SAFE_MKNOD, SAFE_STAT, TST_EXP_EQ_LI, SAFE_UNLINK, SAFE_GETPWNAM, tst_get_free_gid, SAFE_MKDIR, SAFE_CHOWN, SAFE_CHMOD; local functions detected: run, setup; key constants/macros: MODE_RWX, MODE_FIFO_SGID, TEMP_DIR, TEMP_NODE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: run, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: requires a usable nobody account and predictable privilege transitions.

Test signals: TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
