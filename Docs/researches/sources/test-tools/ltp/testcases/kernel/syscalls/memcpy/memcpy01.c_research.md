# sources/test-tools/ltp/testcases/kernel/syscalls/memcpy/memcpy01.c

Purpose: The testcase for buffer copy by check boundary conditions.

Important APIs/types/functions: memcpy, tst_test, tst_res; local functions detected: clearit, fill, checkit, setup, verify_memcpy, run_test; key constants/macros: BSIZE, LEN

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: clearit, fill, checkit, setup, verify_memcpy, run_test.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
