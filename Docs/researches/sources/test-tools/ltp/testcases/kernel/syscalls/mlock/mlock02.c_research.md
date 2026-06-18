# sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock02.c

Purpose: Test for ENOMEM, EPERM errors. 1) mlock(2) fails with ENOMEM if some of the specified address range does not correspond to mapped pages in the address space of the process. 2) mlock(2) fails with ENOMEM if the caller had a non-zero RLIMIT_MEMLOCK soft resource limit, but tried to lock more memory than the limit permitted. This limit is not enforced if the process is privileged (CAP_IPC_LOCK). 3) mlock(2) fails with EPERM if the caller was not privileged (CAP_IPC_LOCK) and its RLIMIT_MEMLOCK soft resource limit was 0.

Important APIs/types/functions: mmap, munmap, mlock, setrlimit, getrlimit, seteuid, tst_test, SAFE_MMAP, SAFE_MUNMAP, TST_EXP_FAIL, SAFE_SETRLIMIT, SAFE_SETEUID, SAFE_GETPWNAM, SAFE_GETRLIMIT; local functions detected: test_enomem1, test_enomem2, test_eperm, run, setup; key constants/macros: No prominent local constants beyond included headers.

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: test_enomem1, test_enomem2, test_eperm, run, setup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; process resource limits adjusted during setup; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking; requires a usable nobody account and predictable privilege transitions.

Test signals: TST_EXP_FAIL errno assertions. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
