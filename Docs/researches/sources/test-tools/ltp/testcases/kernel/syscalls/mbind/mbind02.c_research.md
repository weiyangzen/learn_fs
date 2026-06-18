# sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind02.c

Purpose: We are testing mbind() EIO error. We first fault a allocated page, then attempt to mbind it to a different node. This is a regression test for: a7f40cfe3b7a mm: mempolicy: make mbind() return -EIO when MPOL_MF_STRICT is specified

Important APIs/types/functions: mbind, tst_test, TST_NUMA_MEM, tst_brk, tst_res, TST_RET, TST_ERR, tst_tag, TST_TEST_TCONF; local functions detected: setup, cleanup, verify_policy, verify_mbind; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory; tags link the test to kernel commits/regressions. Local helper functions: setup, cleanup, verify_policy, verify_mbind.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
