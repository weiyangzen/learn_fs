# sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore04.c

Purpose: mincore04 Test shows that pages mapped in one process(parent) and faulted in another(child) results in mincore(in parent) reporting that all mapped pages are resident.

Important APIs/types/functions: open, close, mmap, munmap, mlock, munlock, mincore, ftruncate, fork, fsync, tst_test, SAFE_CLOSE, SAFE_MUNLOCK, SAFE_MUNMAP, SAFE_OPEN, SAFE_FTRUNCATE, SAFE_FSYNC, tst_brk, SAFE_MLOCK, TST_CHECKPOINT_WAKE, TST_CHECKPOINT_WAIT, SAFE_MMAP, SAFE_FORK, tst_reap_children, tst_res; local functions detected: cleanup, setup, lock_file, count_pages_in_cache, test_mincore; key constants/macros: NUM_PAGES

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: cleanup, setup, lock_file, count_pages_in_cache, test_mincore.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: File pages from file creation are cleared from cache.
