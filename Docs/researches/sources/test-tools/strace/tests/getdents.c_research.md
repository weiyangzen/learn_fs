<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getdents.c -->
# sources/test-tools/strace/tests/getdents.c

## Purpose
Covers strace decoder coverage for `getdents`. Source comments describe: Check decoding of getdents syscall. Source read: 48 lines, 1048 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xgetdents.c"; defines: kernel_dirent_type, NR_getdents, STR_getdents; C functions: print_dirent; syscall names/numbers: getdents.

## Control Flow
primary syscall coverage is getdents.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `xgetdents.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getdents.c -->
