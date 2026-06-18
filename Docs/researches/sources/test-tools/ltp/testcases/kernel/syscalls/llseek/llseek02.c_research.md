# sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek02.c

Purpose: Description: 1) lseek(2) fails and sets errno to EINVAL when whence is invalid. 2) lseek(2) fails ans sets errno to EBADF when fd is not an open file descriptor.

Important APIs/types/functions: lseek, open, close, tst_test, TST_RET, tst_res, TST_ERR, tst_strerrno, SAFE_OPEN; local functions detected: verify_llseek, setup; key constants/macros: TEMP_FILE1, TEMP_FILE2, FILE_MODE, SEEK_TOP

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: verify_llseek, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
