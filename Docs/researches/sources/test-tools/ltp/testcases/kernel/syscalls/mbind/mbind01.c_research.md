# sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind01.c

Purpose: use invalid nodemask (64 MiB after heap)

Important APIs/types/functions: mmap, mbind, tst_test, tst_res, tst_brk, tst_kvercmp, SAFE_MMAP, TST_RET, tst_res_hexd, TST_ERR, tst_strerrno, TST_TEST_TCONF; local functions detected: check_policy_pref_or_local, test_default, test_none, test_invalid_nodemask, setup, setup_node, do_test; key constants/macros: MEM_LENGTH, UNKNOWN_POLICY, POLICY_DESC, POLICY_DESC_TEXT

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: check_policy_pref_or_local, test_default, test_none, test_invalid_nodemask, setup, setup_node, do_test.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Check policy of the allocated memory
