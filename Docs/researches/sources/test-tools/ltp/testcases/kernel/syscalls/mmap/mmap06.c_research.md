<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap06.c

## Purpose
This file tests mmap(2) failure errnos for write-only file descriptors, zero length, and missing sharing mode flags.
The source-level description states or implies: Verify that, mmap() call fails with errno: - EACCES, when a file mapping is requested but the file descriptor is not open for reading. - EINVAL, when length argument is 0. - EINVAL, when flags contains none of MAP_PRIVATE, MAP_SHARED, or MAP_SHARED_VALIDATE.

## Important APIs, Types, and Functions
Key local functions: `setup()`, `run()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MALLOC`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TST_EXP_FAIL_PTR_VOID`, `mmap`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 9 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap06.c -->
