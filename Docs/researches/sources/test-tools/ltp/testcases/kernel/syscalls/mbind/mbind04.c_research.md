# sources/test-tools/ltp/testcases/kernel/syscalls/mbind/mbind04.c

Purpose: We are testing mbind() with MPOL_BIND, MPOL_PREFERRED and MPOL_INTERLEAVE For each node with memory we set its bit in nodemask with set_mempolicy() and verify that memory has been faulted accordingly.

Important APIs/types/functions: mbind, fork, tst_test, TST_NUMA_MEM, tst_brk, TST_RET, tst_res, SAFE_FORK, tst_reap_children, TST_TEST_TCONF; local functions detected: setup, cleanup, verify_policy, verify_mbind; key constants/macros: PAGES_ALLOCATED

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: setup, cleanup, verify_policy, verify_mbind.

State and persistence behavior: child process coordination through fork/wait and sometimes LTP checkpoints. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
