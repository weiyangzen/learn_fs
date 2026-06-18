# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise03.c

Purpose: Check that successful madvise(2) MADV_DONTNEED operation will result in zero-fill-on-demand pages for anonymous private mappings.

Important APIs/types/functions: mmap, munmap, madvise, memset, tst_test, TST_RET, tst_brk, tst_res, SAFE_MMAP, SAFE_MUNMAP; local functions detected: run, setup, cleanup; key constants/macros: MAP_SIZE

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: run, setup, cleanup.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: madvise behavior is kernel-version and configuration sensitive, especially newer advice flags.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
