<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap05.c

## Purpose
This file verifies PROT_NONE mappings are created successfully and fault with SIGSEGV when dereferenced.
The source-level description states or implies: Verify that, mmap() call with 'PROT_NONE' and a file descriptor which is open for read and write, succeeds to map the file creating mapped memory, but any attempt to access the contents of the mapped region causes the SIGSEGV signal.

## Important APIs, Types, and Functions
Key local functions: `sig_handler()`, `setup()`, `run()`, `cleanup()`.
Primary syscall/API surface: `mmap`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MALLOC`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_SIGNAL`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `mmap`, `tst_res`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mmap` syscall test directory. LTP mmap syscall coverage using tmpdirs, file descriptors, signals, forks, cgroups, KSM, ext4 mounts, and architecture/kernel feature gates depending on the case.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mmap/mmap05.c -->
