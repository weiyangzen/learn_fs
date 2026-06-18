<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap12.c

## Purpose
This file checks MAP_POPULATE file mappings by consulting pagemap for present pages and verifying zero-filled file contents.
The source-level description states or implies: Verify that mmap() with MAP_POPULATE succeed returning the address of the mapped region. The file should be read into RAM, and pages should be present.

## Important APIs, Types, and Functions
Key local functions: `page_check()`, `verify_mmap()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FTRUNCATE`, `SAFE_LSEEK`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_READ`, `mmap`, `tst_brk`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap12.c -->
