<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap10.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap10.c

## Purpose
This file stress-tests /dev/zero and anonymous mappings, optional KSM mergeability, fork, and partial munmap paths related to THP/rmap bugs.
The source-level description states or implies: This test examines the functionality of mapping and unmapping /dev/zero, which is a common method for allocating anonymous memory in Solaris. The primary objective is to determine whether it is possible to successfully map and unmap /dev/zero, as well as to read from and write to the mapped memory. The design of this test is inspired by two previous bugs, incorporating variations based on their reproducers. Additiona

## Important APIs, Types, and Functions
Key local functions: `run()`, `setup()`.
Primary syscall/API surface: `mmap`, `munmap`, `madvise`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_SYSCONF`, `fork`, `madvise`, `mmap`, `munmap`, `tst_brk`, `tst_reap_children`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.forks_child`, `.needs_root`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 5 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap10.c -->
