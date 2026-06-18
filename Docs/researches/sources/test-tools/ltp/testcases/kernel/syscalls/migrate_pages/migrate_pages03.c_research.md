# sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages03.c

Purpose: Description: This is a regression test for ksm page migration which is miscalculated. The kernel bug has been fixed by: commit 4b0ece6fa0167b22c004ff69e137dc94ee2e469e Author: Naoya Horiguchi <n-horiguchi@ah.jp.nec.com> Date: Fri Mar 31 15:11:44 2017 -0700 mm: migrate: fix remove_migration_pte() for ksm pages

Important APIs/types/functions: mmap, munmap, madvise, mbind, migrate_pages, seteuid, memset, tst_test, tst_brk, SAFE_GETPWNAM, SAFE_MALLOC, SAFE_MMAP, SAFE_FILE_SCANF, SAFE_FILE_PRINTF, SAFE_MUNMAP, SAFE_SETEUID, tst_syscall, tst_res, tst_remaining_runtime, tst_tag, TST_TEST_TCONF; local functions detected: setup, cleanup, migrate_test; key constants/macros: N_PAGES, N_LOOPS, TEST_NODES

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory; tags link the test to kernel commits/regressions. Local helper functions: setup, cleanup, migrate_test.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; requires a usable nobody account and predictable privilege transitions.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
