# sources/test-tools/ltp/testcases/kernel/syscalls/lseek/lseek07.c

Purpose: Description: lseek() succeeds to set the specified offset according to whence and write valid data from this location.

Important APIs/types/functions: lseek, write, read, open, close, memset, tst_test, TST_RET, tst_res, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_CLOSE, SAFE_OPEN, SAFE_READ; local functions detected: verify_lseek, setup, cleanup; key constants/macros: TFILE1, TFILE2, WR_STR1, WR_STR2

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: verify_lseek, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
