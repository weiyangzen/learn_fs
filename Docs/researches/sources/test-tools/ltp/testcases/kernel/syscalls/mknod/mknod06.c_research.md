# sources/test-tools/ltp/testcases/kernel/syscalls/mknod/mknod06.c

Purpose: Verify that mknod(2) fails with the correct error codes: - ENAMETOOLONG if the pathname component was too long. - EEXIST if specified path already exists. - EFAULT if pathname points outside user's accessible address space. - ENOENT if the directory component in pathname does not exist. - ENOENT if the pathname is empty. - ENOTDIR if the directory component in pathname is not a directory.

Important APIs/types/functions: mknod, tst_test, TST_EXP_FAIL, SAFE_MKNOD, tst_buffers; local functions detected: run, setup; key constants/macros: MODE_FIFO_RWX

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: run, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: TST_EXP_FAIL errno assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
