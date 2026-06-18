# sources/test-tools/ltp/testcases/kernel/syscalls/mknodat/mknodat01.c

Purpose: clean created nodes before next run

Important APIs/types/functions: open, close, mknodat, mkdir, unlink, TST_TOTAL, tst_resm, tst_parse_opts, tst_count, tst_exit, tst_sig, tst_tmpdir, tst_get_tmpdir, SAFE_MKDIR, SAFE_OPEN, SAFE_UNLINK, tst_rmdir; local functions detected: verify_mknodat, main, setup, clean, cleanup; key constants/macros: PATHNAME

Control flow: Legacy LTP flow: `main()` parses options, calls setup, loops TEST_LOOPING over testcase entries, invokes verification helpers, then cleanup/tst_exit. Local functions: verify_mknodat, main, setup, clean, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Initialize test dir and file names
