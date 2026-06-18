# sources/test-tools/ltp/testcases/kernel/syscalls/mkdirat/mkdirat01.c

Purpose: DESCRIPTION This test case will verify basic function of mkdirat added by kernel 2.6.16 or up.

Important APIs/types/functions: open, close, mkdir, mkdirat, TST_TOTAL, tst_resm, tst_get_tmpdir, SAFE_MKDIR, SAFE_OPEN, SAFE_CLOSE, tst_parse_opts, tst_count, tst_exit, tst_tmpdir, tst_rmdir; local functions detected: verify_mkdirat, setup_iteration, cleanup_iteration, main, setup, cleanup; key constants/macros: No prominent local constants beyond included headers.

Control flow: Legacy LTP flow: `main()` parses options, calls setup, loops TEST_LOOPING over testcase entries, invokes verification helpers, then cleanup/tst_exit. Local functions: verify_mkdirat, setup_iteration, cleanup_iteration, main, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Initialize test dir and file names
