# sources/test-tools/ltp/testcases/kernel/syscalls/madvise/madvise09.c

Purpose: Check that memory marked with MADV_FREE is freed on memory pressure. o Fork a child and move it into a memory cgroup o Allocate pages and fill them with a pattern o Madvise pages with MADV_FREE o Check that madvised pages were not freed immediately o Write to some of the madvised pages again, these must not be freed o Set memory limits - memory.max = 8MB - memory.swap.max = 16MB The reason for doubling the memory.max is to have safe margin for forking the memory hungy child etc. And the reason to setting memory.swap.max to twice of that is to give the system chance to try to free some memory before cgroup OOM kicks in and kills the memory...

Important APIs/types/functions: mmap, munmap, madvise, fork, wait, tst_test, SAFE_FILE_LINES_SCANF, tst_res, SAFE_CG_PRINTF, tst_cg, SAFE_MMAP, tst_brk, SAFE_FORK, SAFE_WAIT, SAFE_MUNMAP, tst_strstatus, SAFE_CG_HAS, TST_MB; local functions detected: memory_pressure_child, count_freed, check_page_baaa, check_page, child, run, setup; key constants/macros: PAGES, TOUCHED_PAGE1, TOUCHED_PAGE2, MEM_LIMIT, SWAP_LIMIT

Control flow: setup prepares fixtures; test_all runs one whole-file scenario. Local helper functions: memory_pressure_child, count_freed, check_page_baaa, check_page, child, run, setup.

State and persistence behavior: root privileges for namespace, xattr, device, resource-limit, or permission checks; anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; child process coordination through fork/wait and sometimes LTP checkpoints; procfs files parsed for kernel-visible state; memory cgroup limits and counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; kernel madvise advice support for each tested flag; configured cgroup memory controller. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; madvise behavior is kernel-version and configuration sensitive, especially newer advice flags; page size, memory pressure, limits, and overcommit can affect observable residency/locking; process/thread timing is part of the signal and can make failures noisy.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: If swap accounting is disabled exit after process swapped out 100MB Only show memory map if there are issues or for debugging
