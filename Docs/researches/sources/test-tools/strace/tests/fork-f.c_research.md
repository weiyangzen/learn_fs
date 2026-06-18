<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fork-f.c -->
# sources/test-tools/strace/tests/fork-f.c

## Purpose
Covers strace self-test coverage for `fork-f`. Source read: 77 lines, 1420 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <stdio.h>, <string.h>, <unistd.h>, <sys/wait.h>; defines: prefix, logit; C functions: logit_, main.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. process/thread branches use `fork`, `pthread`, pipes, or wait helpers to produce traceable lifecycle events.

## State And Persistence Behavior
child processes or threads are synchronized and reaped before test exit.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: concurrency and process ordering can make trace matching fragile. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fork-f.c -->
