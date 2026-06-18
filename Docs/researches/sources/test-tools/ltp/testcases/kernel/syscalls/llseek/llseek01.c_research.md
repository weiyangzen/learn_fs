# sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek01.c

Purpose: Verify that lseek() call succeeds to set the file pointer position to an offset larger than file size limit (RLIMIT_FSIZE). Also, verify that any attempt to write to this location fails.

Important APIs/types/functions: lseek, write, open, setrlimit, tst_test, TST_RET, tst_res, tst_brk, SAFE_SIGACTION, SAFE_SETRLIMIT, SAFE_OPEN, SAFE_WRITE, SAFE_WRITE_ALL; local functions detected: verify_llseek, setup; key constants/macros: TEMP_FILE, FILE_MODE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: verify_llseek, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; process resource limits adjusted during setup. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
