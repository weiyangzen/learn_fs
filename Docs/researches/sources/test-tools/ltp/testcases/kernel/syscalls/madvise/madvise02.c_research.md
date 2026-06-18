# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise02.c

Purpose: This is a test for the madvise(2) system call. It is intended to provide a complete exposure of the system call. It tests madvise(2) for all error conditions to occur correctly. (A) Test Case for EINVAL 1. start is not page-aligned 2. advice is not a valid value 3. application is attempting to release locked or shared pages (with MADV_DONTNEED) 4. MADV_MERGEABLE or MADV_UNMERGEABLE was specified in advice, but the kernel was not configured with CONFIG_KSM. 8|9. The MADV_FREE & MADV_WIPEONFORK operation can be applied only to private anonymous pages. (B) Test Case for ENOMEM 5|6. addresses in the specified range are not currently mapped or...

Important APIs/types/functions: write, open, close, mmap, munmap, mlock, madvise, fstat, tst_test, tst_brk, tst_kvercmp, SAFE_OPEN, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_FSTAT, SAFE_MMAP, SAFE_MALLOC, SAFE_MUNMAP, SAFE_CLOSE, tst_res, TST_RET, TST_ERR, tst_strerrno; local functions detected: tcases_filter, setup, advice_test, cleanup; key constants/macros: MAP_SIZE, TEST_FILE, STR, TCASE

Control flow: setup prepares fixtures; test iterates over the testcase table; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: tcases_filter, setup, advice_test, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: kernel configured with CONFIG_KSM, skip EINVAL test for MADV_MERGEABLE. In kernel commit 1998cc0, madvise(MADV_WILLNEED) to anon mem doesn't return -EBADF now, as now we support swap prefretch.
