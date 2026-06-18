# sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create02.c

Purpose: Test based on :kselftest:`memfd/memfd_test.c`.

Important APIs/types/functions: close, memfd_create, memset, tst_test, tst_res, TST_ERR, tst_brk, TST_RET, SAFE_CLOSE; local functions detected: setup, verify_memfd_create_errno; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: setup, verify_memfd_create_errno.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; memfd_create and file sealing support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Test memfd_create() syscall Verify syscall-argument validation, including name checks, flag validation and more.
