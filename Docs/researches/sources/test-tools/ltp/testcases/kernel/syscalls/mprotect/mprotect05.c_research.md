<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect05.c

## Purpose
This file regression test for mprotect VMA split and merge behavior over a five-page mapping.
The source-level description states or implies: Testcase to check the mprotect(2) system call split and merge. https://bugzilla.kernel.org/show_bug.cgi?id=217061

## Important APIs, Types, and Functions
Key local functions: `setup()`, `run()`, `cleanup()`.
Primary syscall/API surface: `mprotect`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `SAFE_UNLINK`, `mprotect`, `tst_res`, `tst_tag`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_tmpdir`, `.setup`, `.tags`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mprotect` syscall test directory. mmap/mprotect primitives, legacy LTP signal handling or new harness tags, child processes for SIGSEGV checks, and architecture/compiler cache support in executable tests.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect05.c -->
