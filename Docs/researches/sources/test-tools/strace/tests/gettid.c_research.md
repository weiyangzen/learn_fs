<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/gettid.c -->
# sources/test-tools/strace/tests/gettid.c

## Purpose
Covers strace self-test coverage for `gettid`. Source read: 25 lines, 436 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>, "scno.h", "pidns.h"; defines: none; C functions: main; syscall names/numbers: gettid, __NR_gettid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is gettid, __NR_gettid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; pid namespace translation is sensitive to namespace support and parent/child synchronization. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/gettid.c -->
