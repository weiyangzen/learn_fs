# sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock01.c

Purpose: Test mlock with various valid addresses and lengths.

Important APIs/types/functions: mlock, tst_test, tst_res, SAFE_MALLOC, TST_EXP_PASS; local functions detected: do_mlock, cleanup; key constants/macros: No prominent local constants beyond included headers.

Control flow: test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: do_mlock, cleanup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: TST_EXP_PASS success assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
