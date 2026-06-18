<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages12.c

## Purpose
This file hugetlb race regression suite for move_pages versus hugepage free, soft offline, and migration/fault behavior.
The source-level description states or implies: *Test 1* This is a regression test for the race condition between move_pages() and freeing hugepages, where move_pages() calls follow_page(FOLL_GET) for hugepages internally and tries to get its refcount without preventing concurrent freeing. This test can crash the buggy kernel, and the bug was fixed in: commit e66f17ff71772b209eed39de35aaa99ba819c93d Author: Naoya Horiguchi <n-horiguchi@ah.jp.nec.com> Date: Wed Feb

## Important APIs, Types, and Functions
Key local functions: `do_soft_offline()`, `do_child()`, `do_test()`, `alloc_free_huge_on_node()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`, `move_pages`, `madvise`.
LTP and helper APIs used include: `SAFE_FILE_LINES_SCANF`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`, `SAFE_FORK`, `SAFE_KILL`, `SAFE_MALLOC`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_WAITPID`, `TEST`, `madvise`, `mbind`, `mlock`, `mmap`, `numa_bitmask_alloc`, `numa_bitmask_free`, `numa_bitmask_setbit`, `numa_max_possible_node`, `numa_move_pages`, `tst_brk`, `tst_remaining_runtime`, `tst_res`.
Harness fields present in `struct tst_test`: `.cleanup`, `.forks_child`, `.needs_root`, `.runtime`, `.setup`, `.tags`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 10 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive; temporarily changes resource limits or kernel control files and must restore them; It mutates hugepage pool sysfs state and runs for up to 240 seconds, so cleanup restoration and sufficient free memory are critical..

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages12.c -->
