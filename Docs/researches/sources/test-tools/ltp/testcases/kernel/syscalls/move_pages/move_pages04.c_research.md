<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages04.c

## Purpose
This file validates move_pages per-page status for untouched memory, shared zero page, and invalid address cases.
The source-level description states or implies: Verify that move_pages() properly reports failures when the memory area is not valid, no page is mapped yet or the shared zero page is mapped. [Algorithm] #. Pass the address of a valid memory area where no page is mapped yet (not read/written), the address of a valid memory area where the shared zero page is mapped (read, but not written to) and the address of an invalid memory area as page addresses to move_pages()

## Important APIs, Types, and Functions
Key local functions: `run()`, `setup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `numa_alloc_onnode`, `numa_free`, `numa_move_pages`, `tst_brk`, `tst_res`, `tst_strerrno`, `tst_tag`, `tst_test`.
Harness fields present in `struct tst_test`: `.setup`, `.tags`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages04.c -->
