<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap14.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap14.c

## Purpose
This file checks MAP_LOCKED accounting by comparing VmLck before and after a locked anonymous mapping.
The source-level description states or implies: Verify basic functionality of mmap(2) with MAP_LOCKED. mmap(2) should succeed returning the address of the mapped region, and this region should be locked into memory.

## Important APIs, Types, and Functions
Key local functions: `getvmlck()`, `run()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_FCLOSE`, `SAFE_FOPEN`, `SAFE_MUNMAP`, `SAFE_SSCANF`, `mmap`, `tst_res`, `tst_safe_stdio`, `tst_test`.
Harness fields present in `struct tst_test`: `.needs_root`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap14.c -->
