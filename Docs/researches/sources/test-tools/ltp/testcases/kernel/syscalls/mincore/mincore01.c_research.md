# sources/test-tools/ltp/testcases/kernel/syscalls/mincore/mincore01.c

Purpose: test1: Invoke mincore() when the start address is not multiple of page size. EINVAL test2: Invoke mincore() when the vector points to an invalid address. EFAULT test3: Invoke mincore() when the starting address + length contained unmapped memory. ENOMEM test4: Invoke mincore() when length is greater than (TASK_SIZE - addr). ENOMEM In Linux 2.6.11 and earlier, the error EINVAL was returned for this condition.

Important APIs/types/functions: write, open, close, mmap, munmap, mincore, setrlimit, getrlimit, memset, TST_TOTAL, tst_parse_opts, tst_count, tst_exit, SAFE_MMAP, SAFE_MUNMAP, tst_brkm, SAFE_GETRLIMIT, tst_sig, tst_tmpdir, SAFE_MALLOC, SAFE_OPEN, SAFE_WRITE, SAFE_WRITE_ALL, SAFE_CLOSE, tst_resm, tst_rmdir; local functions detected: main, setup1, setup2, setup3, setup4, setup, mincore_verify, cleanup; key constants/macros: No prominent local constants beyond included headers.

Control flow: Legacy LTP flow: `main()` parses options, calls setup, loops TEST_LOOPING over testcase entries, invokes verification helpers, then cleanup/tst_exit. Local functions: main, setup1, setup2, setup3, setup4, setup, mincore_verify, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; process resource limits adjusted during setup. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: set stack limit so that the unmaped pointer is invalid for architectures like s390 global_pointer will point to a mmapped area of global_len bytes
