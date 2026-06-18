<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap04.c

## Purpose
This file maps anonymous regions with many protection/share combinations and validates /proc/self/maps permission strings.
The source-level description states or implies: Verify that, after a successful mmap() call, permission bits of the new mapping in /proc/pid/maps file matches the prot and flags arguments in mmap() call.

## Important APIs, Types, and Functions
Key local functions: `run()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_FILE_LINES_SCANF`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_SYSCONF`, `mmap`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 15 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap04.c -->
