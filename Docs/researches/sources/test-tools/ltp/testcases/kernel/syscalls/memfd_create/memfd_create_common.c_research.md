# sources/test-tools/ltp/testcases/kernel/syscalls/memfd_create/memfd_create_common.c

Purpose: verify PROT_READ *is* allowed

Important APIs/types/functions: write, read, open, close, mmap, munmap, memfd_create, ftruncate, fallocate, fcntl, mprotect, fstat, pwrite, TST_NO_DEFAULT_MAIN, tst_test, tst_brk_, tst_res_, TST_RET, TST_ERR, SAFE_CLOSE, SAFE_FCNTL; local functions detected: check_fallocate, check_fallocate_fail, check_ftruncate, check_ftruncate_fail, get_mfd_all_available_flags, mfd_flags_available, check_mfd_new, check_mfd_fail_new, check_mmap_fail, check_munmap, check_mfd_has_seals, check_mprotect, check_mfd_fail_add_seals, check_mfd_size, check_mfd_open, check_mfd_fail_open; key constants/macros: TST_NO_DEFAULT_MAIN

Control flow: Control is centered on local helpers check_fallocate, check_fallocate_fail, check_ftruncate, check_ftruncate_fail, get_mfd_all_available_flags, mfd_flags_available, check_mfd_new, check_mfd_fail_new, check_mmap_fail, check_munmap, check_mfd_has_seals, check_mprotect and the surrounding LTP harness.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; memfd_create and file sealing support. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: verify MAP_PRIVATE is *always* allowed (even writable) verify write() succeeds
