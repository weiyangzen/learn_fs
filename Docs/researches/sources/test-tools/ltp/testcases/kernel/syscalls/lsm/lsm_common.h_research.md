# sources/test-tools/ltp/testcases/kernel/syscalls/lsm/lsm_common.h

Purpose: Shared header/support code for the `lsm` LTP syscall tests. It centralizes declarations, constants, or helper routines used by sibling test programs.

Important APIs/types/functions: read, open, close, memset, tst_test, tst_res, SAFE_OPEN, SAFE_CLOSE, tst_lsm_enabled, tst_brk; local functions detected: read_proc_attr, count_supported_attr_current, verify_supported_attr_current; key constants/macros: LSM_GET_SELF_ATTR_H

Control flow: Included by sibling tests; exposes inline/static helpers and shared constants/types. Visible helpers: read_proc_attr, count_supported_attr_current, verify_supported_attr_current.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel LSM syscalls and /sys/kernel/security/lsm when enabled. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
