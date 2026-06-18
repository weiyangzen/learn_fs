<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap07.c

## Purpose
This file MREMAP_DONTUNMAP plus userfaultfd test proving old-address faults are handled by copying data from the new mapping.
The source-level description states or implies: LTP test case for mremap() with MREMAP_DONTUNMAP and userfaultfd. Test mremap() with MREMAP_DONTUNMAP and verify that accessing the old memory region triggers a page fault, which is then correctly handled by a userfaultfd handler.

## Important APIs, Types, and Functions
Key local functions: `check_mremap_dontunmap()`, `setup()`, `cleanup()`, `run()`.
Primary syscall/API surface: `mmap`, `mremap`, `userfaultfd`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_IOCTL`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `SAFE_READ`, `SAFE_USERFAULTFD`, `TST_EXP_EQ_STR`, `mmap`, `mremap`, `pthread_t`, `tst_brk`, `tst_res`, `tst_safe_pthread`, `tst_test`, `userfaultfd`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_checkpoints`, `.needs_kconfigs`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mremap` syscall test directory. mmap/mremap semantics, SysV IPC for mremap04, file-backed mappings, userfaultfd for mremap07, pthreads where needed, and kernel regression tags.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; bad-address tests may differ between libc wrappers and raw syscalls; It relies on CONFIG_USERFAULTFD, checkpoint ordering, and a nonblocking userfaultfd handler; races would produce hangs or false failures..

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap07.c -->
