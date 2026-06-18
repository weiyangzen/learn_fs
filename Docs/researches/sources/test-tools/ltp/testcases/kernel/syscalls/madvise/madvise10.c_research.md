# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise10.c

Purpose: test cases for madvise(2) system call, advise value as "MADV_WIPEONFORK". DESCRIPTION Present the child process with zero-filled memory in this range after a fork(2). The MADV_WIPEONFORK operation can be applied only to private anonymous pages. Within the child created by fork(2), the MADV_WIPEONFORK setting remains in place on the specified map_address range. The MADV_KEEPONFORK operation undo the effect of MADV_WIPEONFORK. Test-Case 1 : madvise with "MADV_WIPEONFORK" flow : Map memory area as private anonymous page. Mark memory area as wipe-on-fork. On fork, child process memory should be zeroed. Test-Case 2 : madvise with "MADV_WIPEONFO...

Important APIs/types/functions: mmap, munmap, madvise, fork, memcpy, tst_test, tst_safe_macros, tst_res, TST_RET, TST_ERR, SAFE_MMAP, SAFE_FORK, tst_reap_children, SAFE_MUNMAP; local functions detected: cmp_area, set_advice, test_madvise, setup; key constants/macros: MAP_SIZE

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: cmp_area, set_advice, test_madvise, setup.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
