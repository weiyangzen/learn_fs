# sources/test-tools/ltp/testcases/kernel/syscalls/llseek/llseek03.c

Purpose: Description: For each of SEEK_SET, SEEK_CUR and SEEK_END verify that, 1. llseek() succeeds to set file position in the middle of the data. The file offset is checked by reading from a file and comparing the data. 2. llseek() succeeds to set file postion to the end of the data, reading this postion returns 0. 3. llseek() succeeds to set file position after the end of the data, reading from this postion returns 0 as well.

Important APIs/types/functions: lseek, write, read, open, close, creat, memset, tst_test, SAFE_CREAT, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_CLOSE, SAFE_OPEN, SAFE_READ, TST_RET, tst_res; local functions detected: setup, verify_lseek; key constants/macros: TEST_FILE, STR

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: setup, verify_lseek.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Seek somewhere in the middle of data Seek to the end of data
