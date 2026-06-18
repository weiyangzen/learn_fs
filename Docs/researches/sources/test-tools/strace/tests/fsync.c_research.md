<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fsync.c -->
# sources/test-tools/strace/tests/fsync.c

## Purpose
Covers strace decoder coverage for `fsync`. Source comments describe: Check decoding of fsync syscall. Source read: 26 lines, 455 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: fsync, __NR_fsync.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is fsync, __NR_fsync.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fsync.c -->
