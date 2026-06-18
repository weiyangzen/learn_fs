# sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock201.c

Purpose: Description: Check the basic functionality of the mlock2(2) since kernel v2.6.9: 1) When we use mlock2() without MLOCK_ONFAULT to lock memory in the specified range that is multiples of page size or not, we can show correct size of locked memory by VmLck from /proc/PID/status and lock all pages including non-present. 2) When we use mlock2() with MLOCK_ONFAULT to lock memory in the specified range that is multiples of page size or not, we can show correct size of locked memory by VmLck from /proc/PID/status and just lock present pages.

Important APIs/types/functions: mmap, munmap, munlock, mlock2, mincore, memset, tst_test, SAFE_MINCORE, SAFE_MMAP, SAFE_FILE_LINES_SCANF, tst_syscall, TST_RET, TST_ERR, tst_res, SAFE_MUNLOCK, SAFE_MUNMAP; local functions detected: check_locked_pages, verify_mlock2, setup; key constants/macros: PAGES, HPAGES

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: check_locked_pages, verify_mlock2, setup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; mlock2 syscall and MLOCK_ONFAULT support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: lock single page, expect it to be locked and present lock all pages, expect all to be locked and present
