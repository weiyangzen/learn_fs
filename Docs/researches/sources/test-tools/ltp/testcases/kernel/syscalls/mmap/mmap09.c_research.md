<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap09.c

## Purpose
This file keeps a file mapped while ftruncate shrinks, grows, and truncates it to zero to ensure the operations succeed.
The source-level description states or implies: Verify that truncating a mmaped file works correctly. Use ftruncate to: 1. shrink the file while it is mapped 2. grow the file while it is mapped 3. zero the size of the file while it is mapped

## Important APIs, Types, and Functions
Key local functions: `verify_mmap()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `ftruncate`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FTRUNCATE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `TST_EXP_PASS`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 4 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap09.c -->
