# sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages01.c

Purpose: errno tests for migrate_pages() syscall

Important APIs/types/functions: mmap, munmap, migrate_pages, fork, waitpid, setuid, memcpy, memset, TST_TOTAL, tst_resm, tst_syscall, tst_get_unused_pid, tst_brkm, SAFE_MUNMAP, SAFE_MALLOC, SAFE_SETUID, SAFE_WAITPID, tst_parse_opts, tst_count, tst_exit, tst_require_root; local functions detected: test_sane_nodes, test_invalid_pid, test_invalid_masksize, test_invalid_mem, test_invalid_nodes, test_invalid_perm, main, setup, cleanup; key constants/macros: No prominent local constants beyond included headers.

Control flow: Legacy LTP flow: `main()` parses options, calls setup, loops TEST_LOOPING over testcase entries, invokes verification helpers, then cleanup/tst_exit. Local functions: test_sane_nodes, test_invalid_pid, test_invalid_masksize, test_invalid_mem, test_invalid_nodes, test_invalid_perm, main, setup, cleanup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; page size, memory pressure, limits, and overcommit can affect observable residency/locking; requires a usable nobody account and predictable privilege transitions; process/thread timing is part of the signal and can make failures noisy.

Test signals: TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: get first node which is not in nodes
