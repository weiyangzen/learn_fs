<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/filter-unavailable.c -->
# sources/test-tools/strace/tests/filter-unavailable.c

## Purpose
Covers strace self-test coverage for `filter-unavailable`. Source read: 63 lines, 1031 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <stdlib.h>, <unistd.h>, <pthread.h>, <sys/wait.h>; defines: P, T; C functions: process, main; struct types: timespec.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations. process/thread branches use `fork`, `pthread`, pipes, or wait helpers to produce traceable lifecycle events.

## State And Persistence Behavior
child processes or threads are synchronized and reaped before test exit.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: concurrency and process ordering can make trace matching fragile. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/filter-unavailable.c -->
