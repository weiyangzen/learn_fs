<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getrandom.c -->
# sources/test-tools/strace/tests/getrandom.c

## Purpose
Covers strace decoder coverage for `getrandom`. Source comments describe: Check decoding of getrandom syscall. syscall/printf are in the inverted order to trigger tcache initialisation first see glibc-2.33.9000-879-gfc859c3. Source read: 47 lines, 1298 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getrandom, __NR_getrandom.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getrandom, __NR_getrandom.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getrandom.c -->
