# sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock05.c

Purpose: Verify mlock() causes pre-faulting of PTEs and prevent memory to be swapped out. Find the new mapping in /proc/$pid/smaps and check Rss and Locked fields after mlock syscall: Rss and Locked size should be equal to the size of the memory allocation

Important APIs/types/functions: mmap, munmap, mlock, munlock, tst_test, tst_safe_stdio, SAFE_FOPEN, SAFE_FCLOSE, tst_brk, SAFE_MMAP, SAFE_MLOCK, TST_EXP_EQ_LU, SAFE_MUNLOCK, SAFE_MUNMAP; local functions detected: get_proc_smaps_info, verify_mlock; key constants/macros: MMAPLEN, LINELEN

Control flow: test_all runs one whole-file scenario. Local helper functions: get_proc_smaps_info, verify_mlock.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: TST_EXP_* value comparisons; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
