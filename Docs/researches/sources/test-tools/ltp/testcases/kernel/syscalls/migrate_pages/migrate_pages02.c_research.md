# sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages02.c

Purpose: use migrate_pages() and check that address is on correct node 1. process A can migrate its non-shared mem with CAP_SYS_NICE 2. process A can migrate its non-shared mem without CAP_SYS_NICE 3. process A can migrate shared mem only with CAP_SYS_NICE 4. process A can migrate non-shared mem in process B with same effective uid 5. process A can migrate non-shared mem in process B with CAP_SYS_NICE

Important APIs/types/functions: mmap, munmap, migrate_pages, fork, waitpid, seteuid, setuid, memset, tst_test, tst_res, SAFE_MALLOC, tst_syscall, TST_RET, SAFE_MMAP, SAFE_MUNMAP, SAFE_FORK, SAFE_SETEUID, SAFE_WAITPID, SAFE_SETUID, tst_brk, TST_CHECKPOINT_WAKE, TST_CHECKPOINT_WAIT, tst_path_val, TST_SR_SKIP_MISSING, TST_SR_TCONF_RO, TST_TEST_TCONF; local functions detected: print_mem_stats, migrate_to_node, addr_on_node, check_addr_on_node, test_migrate_current_process, test_migrate_other_process, run, setup; key constants/macros: NODE_MIN_FREEMEM

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: print_mem_stats, migrate_to_node, addr_on_node, check_addr_on_node, test_migrate_current_process, test_migrate_other_process, run, setup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; requires a usable nobody account and predictable privilege transitions; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: This is an estimated minimum of free mem required to migrate this process to another node as migrate_pages will fail if there is not enough free space on node. While running this test on x86_64 it used ~2048 pages (total VM, not just RSS). Considering ia64 as architecture with largest (non-huge) page size (16k), this limit is set to 2048*16k == 32M. parent can migrate its non-shared memory
