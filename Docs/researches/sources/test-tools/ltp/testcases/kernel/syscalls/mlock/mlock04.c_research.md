# sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock04.c

Purpose: This is a reproducer copied from one of LKML patch submission https://lore.kernel.org/lkml/1296371720-4176-1-git-send-email-tm@tao.ma/ "In 5ecfda0, we do some optimization in mlock, but it causes a very basic test case(attached below) of mlock to fail. So this patch revert it with some tiny modification so that it apply successfully with the lastest 38-rc2 kernel." This bug was fixed by kernel commit fdf4c587a7 ("mlock: operate on any regions with protection != PROT_NONE") As this case does, mmaps a file with PROT_WRITE permissions but without PROT_READ, so attempt to not unnecessarity break COW during mlock ended up causing mlock to fail...

Important APIs/types/functions: open, close, mmap, munmap, mlock, munlock, ftruncate, tst_test, tst_safe_macros, SAFE_MMAP, TST_EXP_PASS, SAFE_MUNLOCK, SAFE_MUNMAP, SAFE_OPEN, SAFE_FTRUNCATE, SAFE_CLOSE, tst_tag; local functions detected: verify_mlock, setup, cleanup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory; tags link the test to kernel commits/regressions. Local helper functions: verify_mlock, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: TST_EXP_PASS success assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
