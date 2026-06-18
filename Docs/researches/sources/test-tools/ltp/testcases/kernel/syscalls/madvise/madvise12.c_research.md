# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise12.c

Purpose: Verify that MADV_GUARD_INSTALL is causing SIGSEGV when someone is accessing memory advised with it. This is a test for feature implemented in 662df3e5c376 ("mm: madvise: implement lightweight guard page mechanism") [Algorithm] - allocate a certain amount of memory - advise memory with MADV_GUARD_INSTALL - access to memory from within a child and verify it gets killed by SIGSEGV - release memory with MADV_GUARD_REMOVE - verify that memory has not been modified before child got killed - modify memory within a new child - verify that memory is accessable and child was not killed by SIGSEGV

Important APIs/types/functions: mmap, munmap, madvise, fork, waitpid, memset, tst_test, TST_KB, TST_EXP_PASS, SAFE_FORK, tst_res, SAFE_WAITPID, tst_strstatus, SAFE_MMAP, SAFE_MUNMAP; local functions detected: run, setup, cleanup; key constants/macros: MAP_SIZE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: run, setup, cleanup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; mount/device availability and filesystem semantics affect read-only and node-creation cases; process/thread timing is part of the signal and can make failures noisy.

Test signals: TST_EXP_PASS success assertions; explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
