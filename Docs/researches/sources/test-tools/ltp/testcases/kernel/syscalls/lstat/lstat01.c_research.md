# sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat01.c

Purpose: Basic test for lstat(): Tests if lstat() writes correct information about a symlink into the stat structure.

Important APIs/types/functions: lstat, symlink, unlink, memset, tst_test, tst_file, tst_syml, TST_RET, tst_res, SAFE_TOUCH, SAFE_SYMLINK, SAFE_UNLINK; local functions detected: run, setup, cleanup; key constants/macros: TESTFILE, TESTSYML

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: run, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
