<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap01.c

## Purpose
This file verifies partial-page file mappings zero-fill bytes past EOF and do not write dirty beyond-EOF bytes back to the file.
The source-level description states or implies: Verify that mmap() succeeds when used to map a file where size of the file is not a multiple of the page size, the memory area beyond the end of the file to the end of the page is accessible. Also, verify that this area is all zeroed and the modifications done to this area are not written to the file. mmap() should succeed returning the address of the mapped region. The memory area beyond the end of file to the end o

## Important APIs, Types, and Functions
Key local functions: `check_file()`, `set_file()`, `run()`, `cleanup()`, `setup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CALLOC`, `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_MMAP`, `SAFE_MSYNC`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_READ`, `SAFE_STAT`, `SAFE_UNLINK`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `mmap`, `tst_brk`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.forks_child`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap01.c -->
