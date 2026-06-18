# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise05.c

Purpose: This is a regression test for madvise(2) system call. It tests kernel for NULL ptr deref Oops fixed by: commit ee53664bda169f519ce3c6a22d378f0b946c8178 Author: Kirill A. Shutemov <kirill.shutemov@linux.intel.com> Date: Fri Dec 20 15:10:03 2013 +0200 mm: Fix NULL pointer dereference in madvise(MADV_WILLNEED) support On buggy kernel with CONFIG_TRANSPARENT_HUGEPAGE=y CONFIG_DEBUG_LOCK_ALLOC=y this testcase should produce Oops and/or be killed. On fixed/good kernel this testcase runs to completion (retcode is 0)

Important APIs/types/functions: mmap, munmap, madvise, mprotect, tst_test, SAFE_MMAP, TST_RET, tst_brk, SAFE_MUNMAP, tst_res, TST_ERR, tst_tag; local functions detected: verify_madvise; key constants/macros: ALLOC_SIZE

Control flow: test_all runs one whole-file scenario; tags link the test to kernel commits/regressions. Local helper functions: verify_madvise.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
