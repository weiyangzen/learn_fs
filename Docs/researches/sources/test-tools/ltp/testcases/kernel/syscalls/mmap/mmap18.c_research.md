<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap18.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap18.c

## Purpose
This file tests MAP_GROWSDOWN stack growth with custom pthread stacks and expected SIGSEGV when growth is blocked.
The source-level description states or implies: Verify mmap() syscall using MAP_GROWSDOWN flag. [Algorithm] **Test 1** We assign the memory region partially allocated with MAP_GROWSDOWN flag to a thread as a stack and expect the mapping to grow when we touch the guard page by calling a recusive function in the thread that uses the growable mapping as a stack. The kernel only grows the memory region when the stack pointer is within guard page when the guard page is

## Important APIs, Types, and Functions
Key local functions: `__attribute__()`, `setup()`, `grow_stack()`, `grow_stack_success()`, `grow_stack_fail()`, `run_test()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_FORK`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `SAFE_WAIT`, `mmap`, `pthread_attr_init`, `pthread_attr_setstack`, `pthread_attr_t`, `pthread_stack`, `pthread_t`, `tst_brk`, `tst_no_corefile`, `tst_res`, `tst_safe_pthread`, `tst_strsig`, `tst_strstatus`, `tst_test`.
Harness fields present in `struct tst_test`: `.forks_child`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap18.c -->
