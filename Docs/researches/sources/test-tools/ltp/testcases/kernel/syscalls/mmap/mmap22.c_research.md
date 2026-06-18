<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap22.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap22.c

## Purpose
This file tests MAP_DROPPABLE reclaim behavior under memory cgroup pressure using mincore.
The source-level description states or implies: Test :manpage:`mmap(2)` with MAP_DROPPABLE flag. Test based on :kselftest:`mm/droppable.c`. Ensure that memory allocated with MAP_DROPPABLE can be reclaimed under memory pressure within a cgroup.

## Important APIs, Types, and Functions
Key local functions: `stress_child()`, `test_mmap()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CG_PRINTF`, `SAFE_FORK`, `SAFE_KILL`, `SAFE_MALLOC`, `SAFE_MINCORE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_WAITPID`, `mmap`, `tst_brk`, `tst_cg`, `tst_cg_drain`, `tst_cg_group`, `tst_cg_group_mk`, `tst_cg_group_rm`, `tst_remaining_runtime`, `tst_res`, `tst_safe_macros`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.forks_child`, `.min_mem_avail`, `.needs_cgroup_ctrls`, `.needs_root`, `.needs_tmpdir`, `.runtime`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 3 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive; temporarily changes resource limits or kernel control files and must restore them; It moves the test into a memory cgroup and kills a pressure child; cgroup drain cleanup is essential..

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap22.c -->
