# sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create03.c

Purpose: Test: Validating memfd_create() with MFD_HUGETLB flag. Test case 1: --WRITE CALL IN HUGEPAGES TEST-- Huge pages are write protected. Any writes to the file should return EINVAL error. Test case 2: --PAGE SIZE OF CREATED FILE TEST-- Default huge page sized pages are created with MFD_HUGETLB flag. Any attempt to unmap memory-mapped huge pages with an unmapping length less than huge page size should return EINVAL error. Test case 3: --HUGEPAGE ALLOCATION LIMIT TEST-- Number of huge pages currently available to use should be atmost total number of allowed huge pages. Memory-mapping more than allowed huge pages should return ENOMEM error.

Important APIs/types/functions: write, close, mmap, munmap, memfd_create, memset, tst_test, SAFE_MMAP, tst_res, SAFE_READ_MEMINFO, SAFE_MUNMAP, tst_brk, SAFE_CLOSE, TST_NEEDS; local functions detected: test_write_protect, test_def_pagesize, test_max_hugepages, memfd_huge_controller; key constants/macros: No prominent local constants beyond included headers.

Control flow: test iterates over the testcase table. Local helper functions: test_write_protect, test_def_pagesize, test_max_hugepages, memfd_huge_controller.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; memfd_create and file sealing support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
